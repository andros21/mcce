# MCCE - Monitor Collect power Consumptions servicE

## :blue_book: Description

I had been given this [electricity monitoring and control system device](https://www.ecodhome.com/en/products/mcee-energy-monitors/), very simple to configure and to use as monitor system (with the integrated LCD display). But a nightmare as control and data analyzer system, because the device is shipped with a closed source (windows exe) software, with ugly UI, to read the stored data using a serial USB connection, with no possibility to interact or export easily the power consumptions.

<img src="https://user-images.githubusercontent.com/58751603/113001400-1388da80-9171-11eb-9386-a413d5fc257e.jpg" alt="drawing" width="380px"/> <img src="https://user-images.githubusercontent.com/58751603/113001740-64003800-9171-11eb-8b57-3b6c0e386cd0.jpg" alt="drawing" width="390px"/>

## :star: Features

So I'd like to turn it into something more advanced:

* Parse the instantaneous values using a Raspberry Pi (im my case a Pi 2) with python script reading from USB serial connector

  > **Note**
  >
  > The first difficulty was to understand how to start the serial flow after the serial connection ... yes, the device not stream nothing by default, a particolar hex code must be send to it to start the bytes streaming. After a little reverse engineering using wireshark usb tool, the code has been found.

  > **Note**
  >
  > The second difficulty was to understand how to read the bytes flow and convert it to decimal values, that must be equal to the power consumptions show by the device display.

  Look at `day_loop.py` for the solutions

* Notify with an alarm tone, when the instantaneous value reach the cap (in my case 4.2 kWh for a max of few minutes) imposed by electricity contract provider

  Below the wiring scheme needed to use `alarm4200.py`

  <img src="https://user-images.githubusercontent.com/58751603/113004677-133e0e80-9174-11eb-96f6-16f800fbacd1.png" alt="drawing" width="430px"/>

  Components:
  * 12V 1A DC
  * Buzzer audio
  * Raspberry Pi 2 (GPIO)
  * [Driver A4988](https://www.amazon.it/Longruner-A4988-Stepstick-dissipatore-stampante-confezione/dp/B071P41ZBW) for step motor (used as audio amplifier)

* Record at the end of the day (midnight) inside database:
  * electric power consumption history with different time resolution
  * electric consumption average

   Look at `day_digest.py`

* With these stats stored, to visualize/analyze them I created simple [dash-app](https://github.com/andros21/pwrApp)

## :rocket: Getting started

The idea is to use a main service `mcce-mcce.service` that must always run, executing `day_loop.py` and only once a day service `mcce-digest.service` to digest/store the power consumption recorded during the day, executing `day_digest.py`

A little description for the last one, it can be started using scheduler as `cron` or more easily using `systemd-timer`, as I do, linked with the service. The are two environment variables that must be set inside `mcce-digest.service`:
 * `$MIN_TIME_RES` the time resolution in minute to use for the power consumptions history of the day
 * `$DATABASE_URL` that can be a file path where the std package `sqlite3` will create and write a local sqlite db every year

By the way, before start with setup, hardware prerequisites:

1. The most difficult: have a MCEE device to hack
2. Raspberry Pi (with a Debian distro)
3. Components needed for the alarm circuit
4. Build the circuit

Steps to run repo/project:

1. Clone the repo
   ```
   git clone https://github.com/andros21/mcce.git
   ```
2. Create a python environment with packages needed
   ```
   poetry install --no-root --only main
   ```
4. Copy systemd service template files inside `/etc/systemd/system/`
5. Change file permissions, that must be `-rw-r-----  root root`
6. Patch them, edit them as you need/want
7. Reload new unit files:
   ```
   sudo systemctl daemon-reload
   ```
8. Enable and start he main service
   ```
   sudo systemctl enable --now mcce-mcce.service
   ```
9. Enable and start the timer that will be triggered at the specify hour/minute, responsible of the related service activation
   ```
   sudo systemctl enable --now mcce-digest.timer
   ```

   > **Warning**
   >
   > Not select an hour before midnight, for `mcce-digest.timer`

9. Check with some `systemctl status` or using `journalctl` if everything went well
10. Enjoy :smile: and not forget to check out related web UI repo [pwrApp](https://github.com/andros21/pwrApp)
