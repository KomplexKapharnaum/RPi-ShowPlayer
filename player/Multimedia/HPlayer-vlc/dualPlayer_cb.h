#pragma once

class dualPlayerCallbacks
{
	public:
    	virtual void onPlayerStateChange(int playerID, int state) = 0;
};