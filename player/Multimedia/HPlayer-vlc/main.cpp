
/*
COMPILE && RUN
g++ hplayer.c -o hplayer -lvlc && ./hplayer
*/
#include <string>
using std::string;

#include <stdio.h>
#include <iostream>
using std::getline;
using std::cout;
using std::cin;

#include <stdlib.h>
#include <unistd.h>

#include <signal.h>
#include "dualPlayer.h"


bool done = false;
dualPlayer *player;

void closeAndQuit(int signum) {
	player->stop();
	player->release();
	exit(signum);
}

int main(int argc, char* argv[])
{
	signal(SIGTERM, closeAndQuit);
	signal(SIGINT, closeAndQuit);

	player = new dualPlayer();

	string input;
	string command;
	string argument;
	while (!done) {
		getline (cin, input);
		command = input.substr(0, input.find(" "));
		if (input.find(" ") != string::npos) argument = input.substr(input.find(" ")+1, input.length());
		else argument = "";

		if (command == "quit") done = true;
		else if (command == "load") player->load(argument);
		else if (command == "play") {
			if (argument.length() == 0) player->play();
			else player->play(argument);
		}
		else if (command == "stop") player->stop();
		else if (command == "pause") player->pause();
		else if (command == "resume") player->resume();
		else if (command == "toggle") player->togglePause();
		else {
			cout << "Typed: " << command << " with arg: " << argument << "\n";
		}

	}
	closeAndQuit(0);

	/*string filepath = "/home/pi/media/vid1.mp4";
	string filepath2 = "/home/pi/media/vid2.mp4";
	player->load(filepath2);
	sleep(5);
	player->play();
	// player->play(filepath);
	sleep(10);


	while(!done) {
		sleep(5);
		player->load(filepath2);
		sleep(5);
		player->play();
		sleep(5);
		player->load(filepath);
		sleep(2);
		player->play();
		done = true;
	}*/
}


/* INFO */
// bool isPlaying() {
// 	return (libvlc_media_player_is_playing(player) == 1);
// }

// void closeAndQuit(int signum) {
// 	stop();	
// 	libvlc_media_player_release (player);
// 	libvlc_release (instance);
	
//  	printf("#PLAYER_EXIT\n");
// 	exit(signum);
// }


/*
libvlc_MediaFreed 

libvlc_MediaPlayerMediaChanged 	
libvlc_MediaPlayerOpening 	
libvlc_MediaPlayerBuffering 	
libvlc_MediaPlayerPlaying 	
libvlc_MediaPlayerPaused 	
libvlc_MediaPlayerStopped 	
libvlc_MediaPlayerEndReached 	

libvlc_MediaListItemAdded 	
libvlc_MediaListItemDeleted 	
libvlc_MediaListWillDeleteItem 	
libvlc_MediaListEndReached 	
 	
libvlc_MediaListPlayerPlayed 	
libvlc_MediaListPlayerNextItemSet 	
libvlc_MediaListPlayerStopped
*/
