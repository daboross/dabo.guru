max_distance = 32;
function set_value(x, y, value) {
    if (x < 0 || x > max_distance || y < 0 || y > max_distance) {
        return
    }
    $("#" + y + "-" + x).text(value);
}
var enemies = []; // list of enemies
var character = {x: 0, y: 0, repr: "X"}; // character position

function animate(x) {
    if (x.hasOwnProperty("old_x") && x.hasOwnProperty("old_y")) {
        if (x.old_x === x.x && x.old_y === x.y) {
            return
        }
        set_value(x.old_x, x.old_y, "");
    }
    set_value(x.x, x.y, x.repr);
    x.old_x = x.x;
    x.old_y = x.y;
}
function update_character() {
    animate(character);
}

function update_enemies() {
    for (var i = 0; i < enemies.length; i++) {
        var enemy = enemies[i];
        enemy.movement(enemy);
        animate(enemy);
    }
}

function spawn_enemy(x, y, repr, movement) {
    enemies[enemies.length] = {x: x, y: y, repr: repr, movement: movement}
}
function rand(max) {
    return Math.floor(Math.random() * max)
}
function spawn_random_enemy() {
    var x, y, repr, movement;
    switch (rand(4)) {
        case 0:
            x = rand(5);
            y = rand(max_distance);
            break;
        case 1:
            x = rand(max_distance);
            y = rand(5);
            break;
        case 2:
            x = max_distance - rand(5);
            y = rand(max_distance);
            break;
        case 3:
            x = rand(max_distance);
            y = max_distance - rand(5);
            break;
    }
    switch (rand(2)) {
        case 0:
            repr = "#";
            movement = function (enemy) {
                var x_dist = character.x - enemy.x;
                var y_dist = character.y - enemy.y;
                if (Math.abs(x_dist) >= Math.abs(y_dist)) {
                    if (x_dist > 0) {
                        enemy.x += 1;
                    } else {
                        enemy.x -= 1;
                    }
                } else {
                    if (y_dist > 0) {
                        enemy.y += 1;
                    } else {
                        enemy.y -= 1;
                    }
                }
            };
            break;
        case 1:
            repr = "%";
            movement = function (enemy) {
                if (!enemy.hasOwnProperty("side")) {
                    enemy.side = rand(4);
                }
                switch (enemy.side) {
                    case 0:
                        enemy.x -= 1;
                        if (enemy.x <= 0) {
                            enemy.side = 2;
                            enemy.x = 0
                        }
                        break;
                    case 1:
                        enemy.y -= 1;
                        if (enemy.y <= 0) {
                            enemy.side = 3;
                            enemy.y = 0;
                        }
                        break;
                    case 2:
                        enemy.x += 1;
                        if (enemy.x >= max_distance) {
                            enemy.side = 0;
                            enemy.x = max_distance;
                        }
                        break;
                    case 3:
                        enemy.y += 1;
                        if (enemy.y >= max_distance) {
                            enemy.side = 1;
                            enemy.y = max_distance;
                        }
                }
            };
            break;
    }
    spawn_enemy(x, y, repr, movement)
}
function main() {
    console.log("Ready!");
    setInterval(update_enemies, 300);
    setInterval(spawn_random_enemy, 5000);
    $(document).keydown(function (event) {
        switch (event.which) {
            case 37:
                character.x -= 1;
                update_character();
                break;
            case 38:
                character.y -= 1;
                update_character();
                break;
            case 39:
                character.x += 1;
                update_character();
                break;
            case 40:
                character.y += 1;
                update_character();
                break;
        }
    });
}

$(document).ready(main);
