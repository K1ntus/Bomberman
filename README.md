
# Bomber Man #

This is a simple "Bomber Man" game written in Python 3, based on the *PyGame* library.

![Bomber Man Snapshot](snap0.png?raw=true "snapshot")


## Download & Install ##

First clone the project available on GitHUB under GPL:

```
  $ git clone https://github.com/orel33/bomber
```

To install Python (root privilege required):

```
  $ sudo apt get install python3 pip3
```

To install the *PyGame* library (user privilege enough):

```
  $ pip3 install pygame
```

To start the game:

```
  $ ./bomber.py
```

By default, the map "maps/map0" is used, but you can generate you own map (*mymap*) and use it as follows:

```
  $ ./bomber.py maps/mymap
```

# Multiplayer #
First, you had to launch the server:

```
  $ ./bomber_server.py <port> <maps/map_you_want_to_use>
  <port> the port you want to use on your server
  <maps/map_you_want_to_use> the map wanted. 

By default, the map "maps/map0” is used.
```
How client connect to server:
```
  $ ./bomber_client.py <host> <port> <nickname>
  <host> the host IP of the server,
  <port> the port you want to use on your server and
  <nickname> the nick wanted
```
## Informations ##
At this step of development, there's few server events:

**Star Rain:**
```
A star (invulnerability for a short amount of time) is randomly generated on the map.
```
**Crazy Fruits:**
```
A random number of fruits (generally few) are dropped around the map.
```
**Ban Hammer:**
```
A bomb is summoned on the feet of each players
```

Independent of the others, there's also an event which is dropping a fixed number of bomb to random position on the map.


## Rules ##

This game is similar to a classic "Bomber Man". This is a *standalone* version of the game for a single player. In this version, a single character (or player) starts the game with an initial amount of 50 health points. Each fruit brings a character with 10 extra health points, while each bomb blast removes 10 health points. A character is dead when its health points reach zero. A character gets immunity for a while after he's hit by a bomb blast. After a character drops a bomb, he is disarmed for a while.

To play, just use the following keys:
  * use *arrows* to move the current character
  * press *space* to drop a bomb at current position, that will explode after a delay of 5 seconds
  * press *escape* to quit the game

The implementation of this game follows a simple MVC architecture (Model/View/Controller).

## Known Bugs ##

There is a [known bug](https://github.com/pygame/pygame/issues/331) in the *pygame.mixer* module, which causes high CPU usage, when calling *pygame.init()*. A workaround is to disable the mixer module, *pygame.mixer.quit()* or not to enable it, by using *pygame.display.init()* and *pygame.font.init()* instead. Consequently, there is no music, no sound :-(

On multiplayer, when a user die, his game freeze and cant see the game progress anymore

## Documentation ##

  * https://www.pygame.org
  * https://openclassrooms.com/courses/interface-graphique-PyGame-pour-python/tp-dk-labyrinthe
  * http://ezide.com/games/writing-games.html

