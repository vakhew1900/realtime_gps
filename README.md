# GPS-SDR-SIM

GPS-SDR-SIM generates GPS baseband signal data streams, which can be converted 
to RF using software-defined radio (SDR) platforms, such as 
[bladeRF](http://nuand.com/), [HackRF](https://github.com/mossmann/hackrf/wiki), and [USRP](http://www.ettus.com/).

### Windows build instructions

1. Start Visual Studio.
2. Create an empty project for a console application.
3. On the Solution Explorer at right, add "gpssim.c" and "getopt.c" to the Souce Files folder.
4. Select "Release" in Solution Configurations drop-down list.
5. Build the solution.

### Building with GCC

```
$ gcc gpssim.c -lm -O3 -o gps-sdr-sim
```

### Generating the GPS signal file

A user-defined trajectory can be specified in either a CSV file, which contains 
the Earth-centered Earth-fixed (ECEF) user positions, or an NMEA GGA stream.
The sampling rate of the user motion has to be 10Hz.
The user is also able to assign a static location directly through the command line.

The user specifies the GPS satellite constellation through a GPS broadcast 
ephemeris file. The daily GPS broadcast ephemers file (brdc) is a merge of the
indiviual site navigation files into one. The archive for the daily file is:

[ftp://cddis.gsfc.nasa.gov/gnss/data/daily/](ftp://cddis.gsfc.nasa.gov/gnss/data/daily/)

These files are then used to generate the simulated pseudorange and
Doppler for the GPS satellites in view. This simulated range data is 
then used to generate the digitized I/Q samples for the GPS signal.

The bladeRF command line interface requires I/Q pairs stored as signed 
16-bit integers, while the hackrf_transfer and gps-sdr-sim-uhd.py
support signed bytes.

HackRF and bladeRF require 2.6 MHz sample rate, while the USRP2 requires
2.5 MHz (an even integral decimator of 100 MHz).

The simulation start time can be specified if the corresponding set of ephemerides
is available. Otherwise the first time of ephemeris in the RINEX navigation file
is selected.

The maximum simulation duration time is defined by USER_MOTION_SIZE to 
prevent the output file from getting too large.

The output file size can be reduced by using "-b 1" option to store 
four 1-bit I/Q samples into a single byte. 
You can use [bladeplayer](https://github.com/osqzss/gps-sdr-sim/tree/master/player)
for bladeRF to playback the compressed file.

```
Usage: gps-sdr-sim [options]
Options:
  -e <gps_nav>     RINEX navigation file for GPS ephemerides (required)
  -u <user_motion> User motion file (dynamic mode)
  -g <nmea_gga>    NMEA GGA stream (dynamic mode)
  -l <location>    Lat,Lon,Hgt (static mode) e.g. 30.286502,120.032669,100
  -t <date,time>   Scenario start time YYYY/MM/DD,hh:mm:ss
  -d <duration>    Duration [sec] (max: 300)
  -o <output>      I/Q sampling data file (default: gpssim.bin)
  -s <frequency>   Sampling frequency [Hz] (default: 2600000)
  -b <iq_bits>     I/Q data format [1/8/16] (default: 16)
  -v               Show details about simulated channels
```

The user motion can be specified in either dynamic or static mode:

```
> gps-sdr-sim -e brdc3540.14n -u circle.csv
```

```
> gps-sdr-sim -e brdc3540.14n -g triumphv3.txt
```

```
> gps-sdr-sim -e brdc3540.14n -l 30.286502,120.032669,100
```

### Transmitting the samples

The TX port of a particular SDR platform is connected to the GPS receiver 
under test through a DC block and a fixed 50-60dB attenuator.

The simulated GPS signal file, named "gpssim.bin", can be loaded
into the bladeRF for playback as shown below:

```
set frequency 1575.42M
set samplerate 2.6M
set bandwidth 2.5M
set txvga1 -25
cal lms
cal dc tx
tx config file=gpssim.bin format=bin
tx start
```

You can also execute these commands via the `bladeRF-cli` script option as below:

```
> bladeRF-cli -s bladerf.script
```

For the HackRF:

```
> hackrf_transfer -t gpssim.bin -f 1575420000 -s 2600000 -a 1 -x 0
```

For UHD supported devices (tested with USRP2 only):

```
> gps-sdr-sim-uhd.py -t gpssim.bin -s 2500000 -x 0
```

## Режим работы в реальном времени

Данное приложение расширяет работу основной утилиты за счет того, что может получать новые данные о местоположении и генерировать новый gps-сигнал
с учетом полученных gps-данных (широты и долготы). GPS-данные ДОЛЖНЫ передоваться по TCP порту (В программе это порт 22500).

Помимо основной утилиты по преобразованию сигнала в данном репозитории присутствубт вспомогательные программы, которые нужны для передачи на порт 22500 gps-данных.

Получать gps-данные можно из:
* Гугл-карт
* gpsd-сервера
* используя дополнительную программу, которая по заданным начальной и конечной точке, а также количеству шагов, составляет маршрут и отправляет его на нужный порт

### Запуск программы

Запуск утилиты по созданию сигнала состоит из трех шагов:
1. Запуск утилиты по преобразованию gps-данных gps-сигнала. 
2. Запуск утилиты вашего SDR (изначально расчитано на HackRF One)
3. Запуск программы, которая выступает Источником gps-данных.

Необходимо соблюдать именно такую последовательность, так как для работы программы, выступающим источником gps-данных необходимо, чтобы порт, на который будут отправляться нужные долгота, широта был открытым, а открывает этот порт Программа для преобразования gps-данных в сигнал.


#### Предварительные настройки 

Для того, чтобы скомпилировать код утилиты, необходимой для преобразования gps-данных в сигнал необходимо выполнить команду:

```
> make
```

Кроме того, необходимо настроить файл gpssim.bin. Для правильной работы программы он должен выступать именнованным программным каналам.
Для этого необходимо воспользоваться командой mkfifo:

```
> mkfifo gpssim.bin
```


#### Запуск утилиты по преобразованию gps-данных gps-сигнала. 
Для запуска основной утилиты необходимо запустить скрипт realtime

```
> ./realtime
```
Этот скрипт является просто красивой оберткой, в котором уже указаны нужные параметры, для запуска программы.

#### Запуск утилиты вашего SDR (изначально расчитано на HackRF One)

Для запуска hackrf_one необходимо написать команду в командной строке

```
> hackrf_transfer -t gpssim.bin -f 1575420000 -s 2600000  -a 1 -x 0
```

или

```
> ./transmit.sh
```

#### Запуск программы, которая выступает Источником gps-данных.

Рассмотрим запуск каждого из вариантов программ, что могут выступать источниками gps-данных

##### Гугл карта
Приложение, которое получает данные гугл-карты и переводит его на нужный порт работает на node.js.
Для его работы необходимо зайти в папку map:
```
> cd map
```

И выполнить команду:
```
> node app.js | nc 127.0.0.1 22500
```
Для передачи координат, необходимо нажимать на нужную кнопку на карте  и тогда сервер будет передавать ее кординаты на нужный порт


#### gpsd-сервер
Для данного способа необходимо чтобы у вас стояла утилита gpsd, а также необходим источник gps данных которые и будут обрабатываться
на gpsd-сервере. 

В случае если вы хотите, чтобы вашим источником данных выступал телефон, то необходимо скачать мобильное приложени 
Share GPS: https://share-gps.ru.aptoide.com/app

Инструкция по работе с Share GPS: https://hackware.ru/?p=10390.

В файле create_gpsd_server.sh меняем HOST на IP вашего телефона. (Переменную PORT в случае необходимости тоже можно поменять)  И запускаем его:

```
> ./create_gpsd_server.sh
```

Теперь наш gpsd сервер работает, но нам необходимо получать с него данные о долготе и широте и передавать их на нужнный порт.
Для этого необходимо запусть python-скрипт:

```
>python3 get_gps_from_tcp.py
```

#### Ипользование дополнительнойпрограммы, которая по заданным начальной и конечной точке, а также количеству шагов, составляет маршрут и отправляет его на нужный порт

В данном репозитории есть программа которая по заданной начальной и конечной точке может простроить маршрут. Кроме того, можно указать промежуточное количество точек, а также время, через которое
на порт будет отправляться новая точка.

```
Аргументы для builRoute.py

-b - Задать стартовуб позицию в формате "широта,долгота"
-e - Задать конечную позицию в формате "широта,долгота"
-s - Количество шагов (промежуточных точек)
--sever - Запустить передачу на нужный порт
-t -  Установить время периода отправки данных на сервер
--csv Создать csv файл с нужными координатам

```

Пример:
```
> python3 buildRoute.py -b 48.0,44.0, -e 55.0,37.0 --server -t 1 -s 400
```

### Замечания
* Программа плохо реагирует в случае если координаты сильно отличаются между собой, поэтому не стоит делать того, чтобы расстояние между двумя точками превышало 10 км (примерно), иначе программа перестанет работать.
* Иногда Share GPS перестает передавать gps-сигнал. Тогда нужно просто выключить передачу gps-данных в приложении и заново его включить
* Иногда при работе с gpsd сервером может отвалится TCP-порт, по которому мы слушаем данные с телефона. Тогда стоит перезапустить наш bash-скрипт.
* При запуске ./realtime может возникнуть проблема 404 Not Found. Причина этого в том, что приложение пытается скачать эфемериды с сайта НАСА, которых еще нет. Тогда необходимо скачать последнюю версию эфемерид с сайта и просто переименовать в тот файл, на который жалуется ./realtime и проблема исчезнет.


### License

Copyright &copy; 2015 Takuji Ebinuma  
Distributed under the [MIT License](http://www.opensource.org/licenses/mit-license.php).
