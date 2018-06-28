use futures::Future;
use {dotenv, fern, log, pb_async, std, tokio};

pub fn logging() {
    let pushbullet_token = dotenv::var("PUSHBULLET_TOKEN");

    // TODO: replace this with standard fern recipe.
    let mut l = fern::Dispatch::new()
        .level(log::LevelFilter::Info)
        .format(|out, msg, record| {
            out.finish(format_args!(
                "[{}][{}] {}",
                record.level(),
                record.target(),
                msg
            ))
        })
        .chain(std::io::stdout());
    if let Ok(token) = pushbullet_token {
        let pb_client =
            pb_async::Client::new(&token).expect("expected pushbullet token to be valid");
        l = l.chain(
            fern::Dispatch::new()
                .level(log::LevelFilter::Warn)
                .filter(|metadata| metadata.target() != "pb-error")
                .chain(fern::Output::call(move |record| {
                    let msg = record.args().to_string();
                    tokio::spawn(
                        pb_client
                            .push(
                                pb_async::PushTarget::SelfUser {},
                                pb_async::PushData::Note {
                                    title: "v2 error",
                                    body: &msg,
                                },
                            )
                            .or_else(|e| {
                                warn!(
                                    target: "pb-error",
                                    "error sending pushbullet error notification: {}",
                                    e,
                                );
                                Ok(())
                            }),
                    );
                })),
        );
    } else {
        warn!("did not find PUSHBULLET_TOKEN env: errors will not be forwarded to pushbullet");
    }
    l.apply().expect("expected to only set up logger once");
}
