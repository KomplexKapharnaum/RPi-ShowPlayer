#pragma once

#include <string>
using std::string;


#include <vlc/vlc.h>
#include "vlcPlayer.h"
#include "dualPlayer_cb.h"

class dualPlayer : public dualPlayerCallbacks
{
	public:
		dualPlayer(int vlc_argc, char const *vlc_argv[]);
		void play(string filepath);
		void load(string filepath);
		void play();
		void stop();
		void pause();
		void resume();
		void togglePause();
		void release();
		void setVolume(int v);

		void onPlayerStateChange(int playerID, int state);
		vlcPlayer* player(int n);
		vlcPlayer *player1;
		vlcPlayer *player2;
		bool running;

	private:
		vlcPlayer* sparePlayer();
		vlcPlayer* activePlayer();

		int selector;
		string filepath;
		int volume;
		libvlc_instance_t *instance;
		pthread_t watcher;
};