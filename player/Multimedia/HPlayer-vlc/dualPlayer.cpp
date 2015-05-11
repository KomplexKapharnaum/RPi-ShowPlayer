#include "dualPlayer.h"
#include "vlcPlayer.h"
#include <unistd.h>
#include <iostream>

dualPlayer::dualPlayer(int vlc_argc, char const *vlc_argv[]):dualPlayerCallbacks()
{
	/* VLC Settings */
	// char const *vlc_argv[] = {
	// 	"--aout", "alsa",
	// 	"--vout", "mmal_vout",
	// 	"--no-osd", //"--no-autoscale",
	// 	"-v"
	// };
	// int vlc_argc = sizeof(vlc_argv) / sizeof(*vlc_argv);
 	//printf("-- CREATE INSTANCE\n");

	for (int i = 0; i < vlc_argc; i++) { // Remember argv[0] is the path to the program, we want from argv[1] onwards
        std::cout << "ARG: " << vlc_argv[i] << "\n";
    }

 	this->instance = libvlc_new (vlc_argc, vlc_argv);
 	//printf("-- CREATE PLAYER 1\n");
 	this->player1 = new vlcPlayer(this->instance, 1, this);
 	//printf("-- CREATE PLAYER 2\n");
 	this->player2 = new vlcPlayer(this->instance, 2, this);
 	this->selector = 1;
}

/* COMMANDS */
void dualPlayer::play(string filepath)
{
	//if (filepath == this->filepath && this->activePlayer()->getState() == PLAYING) this->activePlayer()->rewind();
	this->sparePlayer()->play(filepath);
}

void dualPlayer::load(string filepath)
{
	this->sparePlayer()->load(filepath);
}

void dualPlayer::play()
{
	this->sparePlayer()->play();
}

void dualPlayer::stop()
{
	this->activePlayer()->stop();
}

void dualPlayer::pause()
{
	this->activePlayer()->pause();
}

void dualPlayer::resume()
{
	this->activePlayer()->resume();
}

void dualPlayer::togglePause()
{
	this->activePlayer()->togglePause();
}


void dualPlayer::release()
{
	this->player1->release();
	this->player1->release();
	libvlc_release (this->instance);
 	printf("#PLAYER_EXIT\n");
}

/* EVENTS */
void dualPlayer::onPlayerStateChange(int playerID, int state)
{
	// printf("#PLAYER_STATECHANGE %d %d\n", playerID, state);
	if (state == PLAYING) 
	{
		this->selector = playerID;
		this->activePlayer()->fullScreen();
		this->sparePlayer()->stop();
	}
	if (state == DONE)
	{
		//this->player(playerID)->setState(WAIT);
		//this->player(playerID)->play();
	} 
}


/* INTERNAL */
vlcPlayer* dualPlayer::player(int n)
{
	if (n == 1) return this->player1;
	if (n == 2) return this->player2;
}

vlcPlayer* dualPlayer::activePlayer()
{
	return this->player(this->selector);
}

vlcPlayer* dualPlayer::sparePlayer()
{
	int p;
	if (this->selector == 1) p = 2;
	else p = 1;
	return this->player(p);
}
