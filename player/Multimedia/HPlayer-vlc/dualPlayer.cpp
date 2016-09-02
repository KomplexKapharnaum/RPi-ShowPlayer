#include "dualPlayer.h"
#include "vlcPlayer.h"
#include <unistd.h>
#include <iostream>
#include <pthread.h>
#include <sys/stat.h>
using std::cout;
using std::endl;


// DEBUG PREROLL 
void *watch_end(void* ptr)
{
	dualPlayer* self = reinterpret_cast<dualPlayer*>( ptr );
	//printf("THREAD STARTED\n");
	bool done = false;
	while(!done)
	{
		if (self->player1->getState() == DONE) self->player1->stop();
		if (self->player2->getState() == DONE) self->player2->stop();
		if (!self->running) done = true;
		else usleep(5000);
	}
	return NULL;
}

//APPLY VOLUME DELAYED
void *apply_volume_delayed(void *ptr)
{
	dualPlayer* self = reinterpret_cast<dualPlayer*>( ptr );
	usleep(70000);
	self->applyVolume();
	return NULL;
}

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

	// for (int i = 0; i < vlc_argc; i++) { // Remember argv[0] is the path to the program, we want from argv[1] onwards
 //        std::cout << "ARG: " << vlc_argv[i] << "\n";
 //    }
	this->running = true;
	this->repeat = false;
 	this->instance = libvlc_new (vlc_argc, vlc_argv);
 	//printf("-- CREATE PLAYER 1\n");
 	this->player1 = new vlcPlayer(this->instance, 1, this);
 	//printf("-- CREATE PLAYER 2\n");
 	this->player2 = new vlcPlayer(this->instance, 2, this);
 	this->selector = 1;
 	this->filepath = "";
 	this->volume = 20;

 	pthread_create(&this->watcher, NULL, watch_end, this);
}

/* COMMANDS */
void dualPlayer::play(string filepath)
{
	//if (filepath == this->filepath && this->activePlayer()->getState() == PLAYING) this->activePlayer()->rewind();
	this->filepath = filepath;
	this->sparePlayer()->play(this->filepath);
}

void dualPlayer::load(string filepath)
{
	this->filepath = filepath;
	this->sparePlayer()->load(this->filepath);
}

void dualPlayer::play()
{
	//std::cout << "TRY TO PLAY : " << this->filepath << "\n";
	//printf("STATE SPARE: %d",this->sparePlayer()->getState());

	//unlock loading spare player
	if (this->sparePlayer()->getState() > WAIT) this->sparePlayer()->play();
	//or start spare player with last file used
	else this->sparePlayer()->play(this->filepath);
}

void dualPlayer::stop()
{
	this->setRepeat(false);
	this->activePlayer()->stop();
	this->sparePlayer()->stop();
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

void dualPlayer::applyVolume()
{
	//if (this->activePlayer()->getState() == PLAYING)
		this->activePlayer()->setVolume(this->volume);
	//if (this->sparePlayer()->getState() == PLAYING)
		this->sparePlayer()->setVolume(this->volume);
}

void dualPlayer::setVolume(int v)
{
	if (v >= 0 and v <= 200 and this->volume != v) 
	{
		this->volume = v;
		this->applyVolume();
	}
}

void dualPlayer::volumeUp()
{
	int v = this->volume + VOLUME_STEP;
	if (v > 200) v = 200;
	this->setVolume(v);
}

void dualPlayer::volumeDown()
{
	int v = this->volume - VOLUME_STEP;
	if (v < 0) v = 0;
	this->setVolume(0);
}


void dualPlayer::setRepeat(bool r)
{
	this->repeat = r;
}


void dualPlayer::release()
{
	this->running = false;
	usleep(6000);
	this->player1->release();
	this->player1->release();
	libvlc_release (this->instance);
	cout << "#PLAYER_EXIT" << endl;
 	//printf("#PLAYER_EXIT\n");
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
		pthread_create(&this->applyer, NULL, apply_volume_delayed, this);
	}
	if (state == DONE)
	{
		//this->player(playerID)->setState(WAIT);
		//this->player(playerID)->play();
	}
	if (state == STOPPED)
	{
		this->player(playerID)->setState(WAIT);
		//if this is activePlayer AND sparePlayer not already loading something => try repeat
		if (this->selector == playerID and this->sparePlayer()->getState() == WAIT and this->repeat)
			this->play();
	}
}

void dualPlayer::onFileNotFound()
{
	this->activePlayer()->stop();
}

/* INTERNAL */
vlcPlayer* dualPlayer::player(int n)
{
	if (n == 1) return this->player1;
	if (n == 2) return this->player2;
	return NULL;
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
