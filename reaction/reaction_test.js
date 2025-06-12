const Gpio = require('onoff').Gpio;

const button = new Gpio(17, 'in', 'rising', { debounceTimeout: 10 });
const buzzer = new Gpio(27, 'out');

let testCount = 0;
let failCount = 0;
let isTesting = false;
let startTime = 0;

console.log("Press the button to start reaction test.");

button.watch(function (err, value) {
  if (err) {
    console.log("Button error:", err);
    return;
  }

  if (!isTesting) {
    isTesting = true;
    console.log("Starting reaction test...");
    runTest();
    return;
  }

  if (startTime !== 0) {
    let reactionTime = (Date.now() - startTime) / 1000;
    console.log("Reaction time:", reactionTime.toFixed(3), "seconds");

    if (reactionTime > 0.5) {
      failCount++;
    }

    testCount++;
    startTime = 0;
    buzzer.writeSync(0);

    if (testCount >= 3) {
      endTest();
    } else {
      setTimeout(runTest, 1000);
    }
  }
});

function runTest() {
  let delay = Math.floor(Math.random() * 4000) + 1000;
  console.log("Test " + (testCount + 1) + " is starting soon...");

  setTimeout(function () {
    console.log("Buzzer ON! Press the button!");
    buzzer.writeSync(1);
    startTime = Date.now();

    setTimeout(function () {
      if (startTime !== 0) {
        console.log("No response!");
        buzzer.writeSync(0);
        testCount++;
        startTime = 0;

        if (testCount >= 3) {
          endTest();
        } else {
          setTimeout(runTest, 1000);
        }
      }
    }, 3000);
  }, delay);
}

function endTest() {
  console.log("=== Test finished ===");
  if (failCount > 1) {
    console.log("Drowsy driving suspected. Please take a rest.");
  } else {
    console.log("You are alert. No drowsy driving detected.");
  }

  button.unexport();
  buzzer.unexport();
}
