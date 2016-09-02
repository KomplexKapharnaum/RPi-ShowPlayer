//
// Copyright (c) 2013 Juan Palacios juan.palacios.puyana@gmail.com
// Subject to the BSD 2-Clause License
// - see < http://opensource.org/licenses/BSD-2-Clause>
//

#ifndef CONCURRENT_QUEUE_
#define CONCURRENT_QUEUE_

//#include <queue>
#include <list>
#include <thread>
#include <mutex>
#include <condition_variable>

template <typename T>
class Queue
{
public:
  
  T pop()
  {
    std::unique_lock<std::mutex> mlock(mutex_);
    while (queue_.empty())
    {
      cond_.wait(mlock);
    }
    auto val = queue_.front();
    //queue_.pop();
    queue_.pop_front();
    return val;
  }
  
  void pop(T& item)
  {
    std::unique_lock<std::mutex> mlock(mutex_);
    while (queue_.empty())
    {
      cond_.wait(mlock);
    }
    item = queue_.front();
    //queue_.pop();
    queue_.pop_front();
  }

  bool istexttitreur (const T& value) { return value.find("texttitreur")!=std::string::npos; }
  
  void push(const T& item)
  {
    std::unique_lock<std::mutex> mlock(mutex_);
    //queue_.push(item);
    if(item.find("flushtitreur")!=std::string::npos){
        queue_.remove_if (istexttitreur);
    }else{
        queue_.push_back(item);
    }
    mlock.unlock();
    cond_.notify_one();
  }


    void push_first(const T& item)
  {
    std::unique_lock<std::mutex> mlock(mutex_);
    //queue_.push(item);
    queue_.push_front(item);
    mlock.unlock();
    cond_.notify_one();
  }
  Queue()=default;
  Queue(const Queue&) = delete;            // disable copying
  Queue& operator=(const Queue&) = delete; // disable assignment
  
private:
  //std::queue<T> queue_;
  std::list<T> queue_;
  std::mutex mutex_;
  std::condition_variable cond_;
};

#endif