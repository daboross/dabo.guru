extern crate actix;
extern crate actix_web;
extern crate backoff;
extern crate dotenv;
extern crate failure;
extern crate fern;
extern crate futures;
extern crate http;
extern crate pb_async;
extern crate qutex;
extern crate regex;
extern crate tokio;
extern crate tokio_timer;
extern crate void;
#[macro_use]
extern crate lazy_static;
#[macro_use]
extern crate log;
#[macro_use]
extern crate redis_async;
#[macro_use]
extern crate serde_derive;
#[macro_use]
extern crate failure_derive;

use std::time::Duration;

use actix::prelude::*;
use actix_web::{middleware::Logger, server, App, HttpRequest};
use futures::future;
use futures::Future;
use redis_async::resp::FromResp;

use database::Database;

mod database;
mod redis;
mod setup;
mod statistics;

#[derive(Debug, Fail)]
enum Error {
    #[fail(
        display = "expected at least {} items, found none in redis transaction response", items
    )]
    NotEnough { items: u32 },
}

#[derive(Clone)]
struct AppData {
    conn: Database,
}

fn index(req: HttpRequest<AppData>) -> Box<Future<Item = String, Error = failure::Error>> {
    let fut = req.state()
        .conn
        .transaction(vec![resp_array!["INCR", "test-counter"]])
        .and_then(|res| {
            Ok(format!(
                "Hello, world! Counter: {:?}",
                i64::from_resp(res.into_iter().next().ok_or(Error::NotEnough { items: 1 })?)?
            ))
        });
    Box::new(fut) as Box<Future<Item = _, Error = _>>
}

fn main() {
    actix::System::run(real_server);
}

fn real_server() {
    setup::logging();
    tokio::executor::spawn(future::loop_fn((), |()| {
        info!("starting server");
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

fn create_state() -> impl Future<Item = AppData, Error = failure::Error> {
    Database::new().map(|conn| AppData { conn })
}

fn run_server() -> impl Future<Item = (), Error = failure::Error> {
    create_state().and_then(|state| {
        server::new(move || {
            App::with_state(state.clone())
                .resource("/", |r| r.f(index))
                .resource("/statistics/v1/{plugin_name}/post", |r| {
                    r.method(http::Method::POST)
                        .with(statistics::post_statistics)
                })
                .middleware(Logger::default())
        }).bind("127.0.0.1:8080")?
            .start();
        Ok(())
    })
}
