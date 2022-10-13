# Thimble
A tiny web framework for MicroPython.

## What is it?
Thimble is similar in spirit to Flask, but scaled way back to fit on a microcontroller. Basically, you can create a web application using functions and routes. It's more robust than the typical MicroPython web server example code. But, there's a lot of features it lacks when compared to a full-featured web application fromework. Still, for something that runs on a $15 microcontroller, it's pretty sweet.

## How can I use it?
Copy thimble.py to your MicroPython powered microcontroller. Use main.py to test. Customize with your own functions and routes.

Timble is a class with a route() method and a run() method. You add routes similar to the way you would with Flask and then call a run() method to start listening.

```
from thimble import Thimble

app = Thimble() 

@app.route('/')
def hello(req):
    return 'Hello World'

app.run()
```

Now, point your web browser to the IP of your device on the default port of 80 and you should see 'Hello World'.

Beyond Hello World, here's a more useful example of exposing a GPIO pin via a REST API.

```
from machine import Pin
from thimble import Thimble

gpio_2 = Pin(2, Pin.OUT)

app = Thimble()

@app.route('/gpio/2', methods=['GET'])
def get_gpio_2(req):
    return gpio_2.value()

@app.route('/gpio/2', methods=['PUT'])
def set_gpio_2(req):
    if (body == 1 or body == 'on'):
        gpio_2.on()
    elif (body == 0 or body == 'off'):
        gpio_2.off()
    return gpio_2.value()

app.run(debug=True)  # Listens on 0.0.0.0:80 by default.
```

Saving the code above as main.py will let you read the state of GPIO 2 using a GET method and the URL path of /gpio/2. The same path with a PUT method and `on` or `off` in the request body will change the state of GPIO 2.

Try it out with your favorite REST API client or use the following `curl` commands:

```
curl -X GET -i 'http://192.168.0.43/gpio/2'
curl -X PUT -i 'http://192.168.0.43/gpio/2' --data 0
curl -X PUT -i 'http://192.168.0.43/gpio/2' --data 1
```

You can even get fancier by importing the `json` package so your API can return data like this: `{"value": 125, "units": "millivolts"}` Just change the default content-type to JSON when you instantiate the class. Like this: 

```
app = Thimble(default_content_type='application/json')
```

See [the wiki](https://github.com/DavesCodeMusings/thimble/wiki) for more examples in a step by step tutorial format.

## What pitfalls do I need to be aware of?
Using the example main.py assumes that networking is already configured by a boot.py that you supply. Thimble won't work without it. If you need help with wifi connections, see my example under [lolin32oled](https://github.com/DavesCodeMusings/esp/tree/main/lolin32oled)

Thimble is in the beginning phases of development and may crash from time to time. If it does, add a Github issue and I'll see if I can fix it.

## Will it run on Microcontroller X?
Code is being developed and tested using a Wemos LOLIN32 (ESP32) clone with MicroPython 1.19.1. Occasionally, I will run it on a Wemos D1 Mini (ESP8266) clone. It may or may not work with other devices.
