extern crate actix;
extern crate actix_web;
extern crate failure;
extern crate void;
#[macro_use]
extern crate log;
extern crate fern;
extern crate futures;
extern crate qutex;
extern crate tokio_timer;
#[macro_use]
extern crate redis_async;
extern crate backoff;
extern crate tokio;

use std::time::Duration;

use futures::future;
use futures::Future;
use tokio::reactor::Handle;

use actix::prelude::*;
use actix_web::{middleware::Logger, server, App, HttpRequest, Responder};
use backoff::{backoff::Backoff, ExponentialBackoff};
use redis_async::client::{paired_connect, PairedConnection};
use redis_async::resp::RespValue;
use tokio::executor;

use redis::RedisActor;

mod redis;

#[derive(Clone)]
struct AppData {
    conn: Addr<RedisActor>,
}

fn index(req: HttpRequest<AppData>) -> Box<Future<Item = String, Error = failure::Error>> {
    let fut = req.state()
        .conn
        .send(redis::message(resp_array!["INCR", "test-counter"]))
        .then(|res| res.map_err(Into::into).and_then(|v| v))
        .map_err(|e| {
            warn!("error handling indx: {}", e);
            e
        })
        .map(|counter: i64| format!("Hello, world! Counter: {}", counter));
    Box::new(fut) as Box<Future<Item = _, Error = _>>
}

fn main() {
    setup_logging();
    info!("starting server");
    actix::System::run(real_server);
}

fn real_server() {
    tokio::executor::spawn(future::loop_fn((), |()| {
        run_server().then(|res| match res {
            Ok(()) => {
                info!("server started successfully");
                future::Either::A(future::ok(future::Loop::Break(())))
            }
            Err(e) => {
                warn!("server error while starting: {}", e);
                info!("trying again in 30 seconds...");
                future::Either::B(
                    tokio_timer::sleep(Duration::from_secs(30))
                        .then(|_| Ok(future::Loop::Continue(()))),
                )
            }
        })
    }));
}

fn setup_logging() {
    // TODO: replace this with standard fern recipe.
    fern::Dispatch::new()
        .level(log::LevelFilter::Info)
        .format(|out, msg, record| {
            out.finish(format_args!(
                "[{}][{}] {}",
                record.level(),
                record.target(),
                msg
            ))
        })
        .chain(std::io::stdout())
        .apply()
        .expect("expected to only set up logger once");
}

fn create_state() -> impl Future<Item = AppData, Error = failure::Error> {
    RedisActor::new()
        .from_err()
        .map(|conn| AppData { conn: conn.start() })
}

fn run_server() -> impl Future<Item = (), Error = failure::Error> {
    create_state().and_then(|state| {
        server::new(move || {
            App::with_state(state.clone())
                .resource("/", |r| r.f(index))
                .middleware(Logger::default())
        }).bind("127.0.0.1:8080")?
            .start();
        Ok(())
    })
}
