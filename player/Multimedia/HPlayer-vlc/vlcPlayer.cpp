#include "vlcPlayer.h"
#include "main.h"
#include <sys/time.h>
#include <unistd.h>
#include <inttypes.h>
#include <pthread.h>

/* TIME MEASURE */
unsigned long long mstime() {
	struct timeval tv;

	gettimeofday(&tv, NULL);

	unsigned long long millisecondsSinceEpoch =
	    (unsigned long long)(tv.tv_sec) * 1000 +
	    (unsigned long long)(tv.tv_usec) / 1000;

	return millisecondsSinceEpoch;
}

// DEBUG PREROLL 
void *wait_preroll(void* ptr)
{
	vlcPlayer* self = reinterpret_cast<vlcPlayer*>( ptr );
	printf("THREAD STARTED\n");
	self->wait_preroll();
}


/* EVENTS */
void vlcCallbacks( const libvlc_event_t* event, void* ptr )
{
	vlcPlayer* self = reinterpret_cast<vlcPlayer*>( ptr );
	// printf("-- EVENT ON PLAYER %d\n", self->getId());
    switch ( event->type )
    {

	    case libvlc_MediaPlayerVout:
	        // printf("#MEDIA_VOUT %d\n", self->getId());
			//printf("VOUT %llu\n",mstime());
			if (self->locked()) 
			{
				self->pause();
				self->setState(READY);
			}
			else self->setState(PLAYING);
	        break;

	    case libvlc_MediaPlayerPaused:
			//printf("#MEDIA_PAUSE %d\n", self->getId());
	        break;
	    
	    case libvlc_MediaPlayerStopped:
			if (self->getState() == PLAYING) 
			{ 
				printf("#MEDIA_END %d\n", self->getId());
	    		//self->stop();
	    	}
	    	//printf("#MEDIA_END\n");
			self->setState(WAIT);
	        break;
    
	    case libvlc_MediaPlayerEndReached:
	    	//printf("#MEDIA_FINNISHED %d\n", self->getId());
	        printf("#MEDIA_FINNISHED\n");
	        break;

	    case libvlc_MediaPlayerBuffering:
	    	//printf("BUFFERING %llu\n",mstime());
	    	break;

	    case libvlc_MediaPlayerPlaying:
	    	//printf("PLAYING %llu\n",mstime());
	    	break;

	    // case libvlc_MediaPlayerTimeChanged:
	    // case libvlc_MediaPlayerPositionChanged:
	    // case libvlc_MediaPlayerLengthChanged:
	    // case libvlc_MediaPlayerSnapshotTaken:
	    // case libvlc_MediaPlayerEncounteredError:
	    // case libvlc_MediaPlayerSeekableChanged:
	    // case libvlc_MediaPlayerPausableChanged:
	    // case libvlc_MediaPlayerTitleChanged:
	    // case libvlc_MediaPlayerNothingSpecial:
	    // case libvlc_MediaPlayerOpening:
	    // case libvlc_MediaPlayerForward:
	    // case libvlc_MediaPlayerBackward:
	    default:
	        break;
    }
}

int i;
vlcPlayer::vlcPlayer(libvlc_instance_t *instance, int id, dualPlayerCallbacks *cb)
{
	this->state == WAIT;
	this->id = id;
	this->instance = instance;
	this->callback = cb;
	this->lock = false;
	this->player = libvlc_media_player_new (this->instance);
	this->eventsManager = libvlc_media_player_event_manager(this->player);
	// libvlc_event_attach(this->eventsManager, libvlc_MediaPlayerOpening, (libvlc_callback_t)this->onOpen, NULL);
	libvlc_event_attach(this->eventsManager, libvlc_MediaPlayerBuffering, vlcCallbacks, this);
	libvlc_event_attach(this->eventsManager, libvlc_MediaPlayerVout, vlcCallbacks, this);
	libvlc_event_attach(this->eventsManager, libvlc_MediaPlayerPlaying, vlcCallbacks, this);
	libvlc_event_attach(this->eventsManager, libvlc_MediaPlayerPaused, vlcCallbacks, this);
	libvlc_event_attach(this->eventsManager, libvlc_MediaPlayerStopped, vlcCallbacks, this);
	libvlc_event_attach(this->eventsManager, libvlc_MediaPlayerEndReached, vlcCallbacks, this);
}

/* COMMANDS */
void vlcPlayer::load(string filepath, bool lock)
{
	this->setState(LOADING);
	this->lock = lock;
	this->media = libvlc_media_new_path (this->instance, filepath.c_str());
	libvlc_media_player_set_media(this->player, media);
	libvlc_media_player_play (this->player);
}

void vlcPlayer::load(string filepath)
{
	this->load(filepath, true);
}

void vlcPlayer::play(string filepath)
{
	this->load(filepath, false);
}

void vlcPlayer::play()
{
	this->lock = false;
	// printf("#STATE of PLAYER%d: %d\n",this->getId(),this->state);
	if (this->state == READY) 
	{
		// printf("PLAY GO %llu\n",mstime());
		// printf("position: %f\n", libvlc_media_player_get_position(this->player));
		// printf("time: %"PRId64"\n", libvlc_media_player_get_time(this->player));
		this->resume();
		this->setState(PLAYING);
	}
	else if (this->state == PLAYING)
	{
		this->replay();
	}
}

void vlcPlayer::replay()
{
	libvlc_media_player_set_position(this->player, 0.0);
	//libvlc_media_player_set_time(this->player, 0);
}

void vlcPlayer::pause()
{
	libvlc_media_player_set_pause (this->player, 1);
}

void vlcPlayer::resume()
{
	libvlc_media_player_set_pause (this->player, 0);
}

void vlcPlayer::togglePause()
{
	libvlc_media_player_pause (this->player);
}

void vlcPlayer::stop()
{
	if (this->getState() > WAIT)  libvlc_media_player_stop (this->player);
}

void vlcPlayer::release()
{
	//this->stop();
	libvlc_media_player_release (this->player);
}

int vlcPlayer::getState()
{
	return this->state;
}

void vlcPlayer::setState(int state)
{
	this->state = state;
	//if (this->state == WAIT) printf("#PLAYER_WAIT %d\n",this->getId());
	//if (this->state == LOADING) printf("#PLAYER_LOADING %d\n",this->getId());
	//if (this->state == READY) printf("#PLAYER_READY %d\n",this->getId());
	//if (this->state == PLAYING) printf("#MEDIA_PLAY %d\n",this->getId());
	if (this->state == PLAYING) printf("#MEDIA_PLAY\n");
	this->callback->onPlayerStateChange(this->getId(), this->state);
}

bool vlcPlayer::locked() 
{
	return this->lock;
}

int vlcPlayer::getId()
{
	return this->id;
}

void vlcPlayer::fullScreen()
{
	//libvlc_set_fullscreen(this->player, 1);
}

void vlcPlayer::wait_preroll() 
{
	while(libvlc_media_player_get_time(this->player) == 0)
	{
		printf("wait for video to begin %llu\n",mstime());
		printf("vout %d\n",libvlc_media_player_has_vout(this->player));
		
		pthread_yield();
		usleep(2000);
	}
	long long p = 0;
	while(true)
	{
		if (p != libvlc_media_player_get_time(this->player)) printf("time %llu\n",libvlc_media_player_get_time(this->player));
		p = libvlc_media_player_get_time(this->player);
		pthread_yield();
		usleep(2000);
	}
	printf("video time: %llu\n",libvlc_media_player_get_time(this->player));

}