#pragma once

#include <string>
using std::string;


#include <vlc/vlc.h>
#include "vlcPlayer.h"
#include "dualPlayer_cb.h"

class dualPlayer : public dualPlayerCallbacks
{
	public:
		dualPlayer();
		void play(string filepath);
		void load(string filepath);
		void play();
		void stop();
		void pause();
		void resume();
		void togglePause();
		void release();

		void onPlayerStateChange(int playerID, int state);
		vlcPlayer* player(int n);

	private:
		vlcPlayer* sparePlayer();
		vlcPlayer* activePlayer();

		int selector;
		libvlc_instance_t *instance;
		vlcPlayer *player1;
		vlcPlayer *player2;
};