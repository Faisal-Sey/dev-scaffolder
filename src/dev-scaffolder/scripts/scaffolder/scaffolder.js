import { createInterface } from "readline";

const rl = createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: true
})

rl.question("What is your name? ", (name) => {
    console.log(`Hello ${name}!`);
    rl.question("What is your favorite color? ", (color) => {
        console.log(`Your favorite color is ${color}!`);
        rl.close();
    })
})