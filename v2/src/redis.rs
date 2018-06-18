use std::net;
use std::time::Duration;

use actix::prelude::*;
use actix::AsyncContext;
use backoff::{backoff::Backoff, ExponentialBackoff};
use futures::{future, Future};
use redis_async::{client::{paired_connect, PairedConnection},
                  resp::{FromResp, RespValue}};
use std::marker::PhantomData;
use tokio::executor;
use void::Void;
use {failure, tokio_timer};

pub fn message<R: FromResp>(msg: RespValue) -> RedisMessage<R> {
    RedisMessage(msg, PhantomData)
}

#[derive(Debug, Clone)]
pub struct RedisMessage<R>(pub RespValue, PhantomData<R>)
where
    R: FromResp;

impl<R> Message for RedisMessage<R>
where
    R: FromResp + Send + 'static,
{
    type Result = Result<R, failure::Error>;
}

pub struct RedisActor {
    conn: PairedConnection,
    /// We need this since the "successfull reconnection" method uses a message
    /// to initiate the reconnection and we need to delay any other messages
    /// which happen in the meantime until after that message comes through.
    reconnecting: bool,
}

impl Actor for RedisActor {
    type Context = Context<Self>;
}

struct DoReconnect;
impl Message for DoReconnect {
    type Result = ();
}
struct SuccessfullyReconnected(PairedConnection);
impl Message for SuccessfullyReconnected {
    type Result = ();
}
struct UnsuccessfullReconnect;
impl Message for UnsuccessfullReconnect {
    type Result = ();
}

impl RedisActor {
    fn local_host() -> net::SocketAddr {
        net::SocketAddr::new(
            net::IpAddr::V6(net::Ipv6Addr::new(0, 0, 0, 0, 0, 0, 0, 1)),
            6379,
        )
    }
    pub fn new() -> impl Future<Item = Self, Error = Void> {
        RedisActor::connect().map(|conn| RedisActor {
            conn,
            reconnecting: false,
        })
    }
    fn connect() -> impl Future<Item = PairedConnection, Error = Void> {
        let mut backoff = ExponentialBackoff::default();
        // we're willing to wait up to 30 minutes
        backoff.max_interval = Duration::from_secs(60 * 30);
        backoff.max_elapsed_time = None;
        future::loop_fn(backoff, |mut backoff| {
            let addr = RedisActor::local_host();
            paired_connect(&addr).then(move |res| match res {
                Ok(conn) => future::Either::A(future::ok(future::Loop::Break(conn))),
                Err(e) => {
                    let retry = backoff.next_backoff().unwrap();
                    error!(
                        "unable to connect to redis database at {:?}: {}. Retrying in {:?}.",
                        addr, e, retry
                    );
                    future::Either::B(
                        tokio_timer::sleep(retry)
                            .then(|_| future::ok(future::Loop::Continue(backoff))),
                    )
                }
            })
        })
    }
    fn start_reconnect(&mut self, ctx: &mut Context<Self>) {
        let my_addr = ctx.address();
        let fut = RedisActor::connect().then(move |res: Result<_, Void>| match res {
            Ok(conn) => {
                executor::spawn(my_addr.send(SuccessfullyReconnected(conn)).then(|_| Ok(())));
                future::ok(())
            }
            Err(e) => match e {},
        });
        self.reconnecting = true;
        AsyncContext::wait(ctx, actix::fut::wrap_future(fut));
    }
}

impl Handler<SuccessfullyReconnected> for RedisActor {
    type Result = ();

    fn handle(
        &mut self,
        SuccessfullyReconnected(conn): SuccessfullyReconnected,
        _ctx: &mut Context<Self>,
    ) {
        self.conn = conn;
        self.reconnecting = false;
    }
}

impl Handler<UnsuccessfullReconnect> for RedisActor {
    type Result = ();

    fn handle(&mut self, _: UnsuccessfullReconnect, ctx: &mut Context<Self>) {
        self.reconnecting = false;
        ctx.stop();
    }
}

impl Handler<DoReconnect> for RedisActor {
    type Result = ();

    fn handle(&mut self, _: DoReconnect, ctx: &mut Context<Self>) {
        self.start_reconnect(ctx);
    }
}

impl<R> Handler<RedisMessage<R>> for RedisActor
where
    R: FromResp + Send + 'static,
{
    type Result = ResponseFuture<R, failure::Error>;

    fn handle(
        &mut self,
        RedisMessage(msg, _): RedisMessage<R>,
        ctx: &mut Context<Self>,
    ) -> Self::Result {
        use redis_async::error::Error;

        fn resend_self<R: FromResp + Send + 'static>(
            address: Addr<RedisActor>,
            msg: RespValue,
        ) -> impl Future<Item = R, Error = failure::Error> {
            address.send(message(msg)).then(|res| match res {
                Ok(r) => r,
                Err(e) => Err(e.into()),
            })
        }

        if self.reconnecting {
            Box::new(resend_self(ctx.address(), msg))
        } else {
            let addr = ctx.address();
            // Clone is necessary so we can re-send the message if the connection is closed.
            let fut = self.conn.send(msg.clone()).or_else(|e| match e {
                Error::EndOfStream => future::Either::A(
                    addr.send(DoReconnect)
                        .from_err()
                        .and_then(|()| resend_self(addr, msg)),
                ),
                o => future::Either::B(future::err(o.into())),
            });

            Box::new(fut) as ResponseFuture<_, _>
        }
    }
}
