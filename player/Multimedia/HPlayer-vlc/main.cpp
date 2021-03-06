#include "main.h"
using std::endl;
/*
COMPILE && RUN
g++ hplayer.c -o hplayer -lvlc && ./hplayer
*/

// Close players and quit
void closeAndQuit(int signum) {
	player->stop();
	player->release();
	usleep(100000);
	exit(signum);
}

// Parse STDIN commands
void parseInput(string input) {
	string command;
	string argument;
	command = input.substr(0, input.find(" "));
	if (input.find(" ") != string::npos) argument = input.substr(input.find(" ")+1, input.length());
	else argument = "";

	if (command == "quit") running = false;
	else if (command == "load") player->load(argument);
	else if (command == "play") {
		if (argument.length() == 0) player->play();
		else player->play(argument);
	}
	else if (command == "stop") player->stop();
	else if (command == "pause") player->pause();
	else if (command == "resume") player->resume();
	else if (command == "toggle") player->togglePause();
	else if (command == "repeat") {
		if (argument == "1") player->setRepeat(true);
		else if (argument == "0") player->setRepeat(false);
		else cout << "#REPEAT_ERROR " << argument << "\n";
	}
	else if (command == "volume") 
	{
		//cout << "#VOLUME_SUPPLIED " << argument << endl;
		std::string::size_type sz;
		int vol = atoi(argument.c_str());
		if (vol >= 0 and vol <= 200) player->setVolume(vol);
		else cout << "#VOLUME_ERROR " << argument << "\n";
	}
	else if (command == "volup") player->volumeUp();
	else if (command == "voldown") player->volumeDown();
	else {
		cout << "Unknown command: " << command << " with arg: " << argument << "\n";
	}
}

//keep reading standard input
void readcin(Queue* q) {
  string input;
  while (running) {
    getline(cin, input);
    if(input.length()>3) q->push(input);
    if (input == "quit") running = false;
  }
}

//threaded function to pop the Queue
void* consume(void *ptr) {
	Queue* q = reinterpret_cast<Queue*>( ptr );
	while (running) {
		auto item = q->pop();
		parseInput(item);
	}
	return NULL;
}

//main
int main(int argc, char* argv[])
{
	signal(SIGTERM, closeAndQuit);
	signal(SIGINT, closeAndQuit);

	running = true;

	char const *vlc_argv[argc];
	for (int i = 1; i < argc; ++i) { // Remember argv[0] is the path to the program, we want from argv[1] onwards
        vlc_argv[i-1] = argv[i];
    }
	player = new dualPlayer(argc-1, vlc_argv);
	inputQueue = new Queue();


	pthread_create(&consumer, NULL, consume, inputQueue);
	readcin(inputQueue);
	pthread_join(consumer,NULL);
  	closeAndQuit(0);
}


// RC Interface
/*
+----[ CLI commands ]
| play . . . . . . . . . . . . . . . . . . . . . . . . . . play stream
| stop . . . . . . . . . . . . . . . . . . . . . . . . . . stop stream
| repeat [on|off]  . . . . . . . . . . . . . .  toggle playlist repeat
| loop [on|off]  . . . . . . . . . . . . . . . .  toggle playlist loop
| seek X . . . . . . . . . . . seek in seconds, for instance `seek 12'
| pause  . . . . . . . . . . . . . . . . . . . . . . . .  toggle pause
| is_playing . . . . . . . . . . . .  1 if a stream plays, 0 otherwise
| get_title  . . . . . . . . . . . . . the title of the current stream
| get_length . . . . . . . . . . . .  the length of the current stream
| 
| volume [X] . . . . . . . . . . . . . . . . . .  set/get audio volume
| volup [X]  . . . . . . . . . . . . . . .  raise audio volume X steps
| voldown [X]  . . . . . . . . . . . . . .  lower audio volume X steps
| quit . . . . . . . .  quit VLC (or logout if in a socket connection)
| shutdown . . . . . . . . . . . . . . . . . . . . . . .  shutdown VLC
+----[ end of help ]
*/


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
