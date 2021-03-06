#pragma once

#include <string>
using std::string;

#include <vlc/vlc.h>
#include "dualPlayer_cb.h"

#define WAIT 0
#define LOADING 1
#define READY 2
#define PLAYING 3
#define DONE 4
#define STOPPED 5

class vlcPlayer 
{
	public:
		vlcPlayer(libvlc_instance_t *instance, int id, dualPlayerCallbacks *cb);
		void play(string filepath);
		void load(string filepath);
		void play();
		void pause(); 
		void resume();
		void togglePause();
		void stop();
		void rewind();
		void endclear();
		void release();
		void setState(int state);
		int getState();
		bool locked();
		int getId();
		void fullScreen();
		void setVolume(int v);
		// void callbacks( const libvlc_event_t* event, void* ptr );
		libvlc_media_player_t *player;

	private:
		bool load(string filepath, bool lock);

		int id;
		int state;
		bool lock;
		libvlc_instance_t *instance;
		dualPlayerCallbacks *callback;
		libvlc_event_manager_t *eventsManager;
		//libvlc_media_t *media;	
		string filepath;
};