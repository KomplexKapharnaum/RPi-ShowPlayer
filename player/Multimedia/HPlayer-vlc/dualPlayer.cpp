#include "dualPlayer.h"
#include "vlcPlayer.h"
#include <unistd.h>

dualPlayer::dualPlayer():dualPlayerCallbacks()
{
	/* VLC Settings */
	char const *vlc_argv[] = {
		"--aout", "alsa",
		"--vout", "mmal_vout",
		"--no-osd", "--no-autoscale",
		//"-v"
	};
	int vlc_argc = sizeof(vlc_argv) / sizeof(*vlc_argv);
 	//printf("-- CREATE INSTANCE\n");
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
