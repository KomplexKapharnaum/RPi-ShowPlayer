#include <Python.h>
#include <time.h>
#include <math.h>

static PyObject *
rtplib_set_time(PyObject *self, PyObject *args){
    /*
        Set time system from python
    */
    struct timespec time;
	if (!PyArg_ParseTuple(args, "ii", &time.tv_sec, &time.tv_nsec)) // Get time from python
	        return NULL;
	return Py_BuildValue("i", clock_settime(CLOCK_REALTIME, &time));
}


static PyObject *
rtplib_get_time(PyObject *self, PyObject *args){
    /*
        Get time system for python
    */
    struct timespec time;
    clock_gettime(CLOCK_REALTIME, &time);
	return Py_BuildValue("ii", time.tv_sec, time.tv_nsec);
}


static PyObject *
rtplib_remain_time(PyObject *self, PyObject *args){
    /*
        Get time system for python
    */
    struct timespec time, current_time;
    if (!PyArg_ParseTuple(args, "ii", &time.tv_sec, &time.tv_nsec)) // Get time from python
	        return NULL;
	clock_gettime(CLOCK_REALTIME, &current_time);
	return Py_BuildValue("ii", current_time.tv_sec-time.tv_sec, current_time.tv_nsec-time.tv_nsec);
}


static PyObject *
rtplib_add_time(PyObject *self, PyObject *args){
    int tv_sec, tv_nsec, add_sec, add_nsec;
    float    add_time;
    if (!PyArg_ParseTuple(args, "iif", &tv_sec, &tv_nsec, &add_time)) // Get time from python
	        return NULL;
	add_sec = (int)(add_time);
	add_nsec = (int)((add_time-(int)(add_time))*1000000000);
	tv_sec += add_sec + (int)((tv_nsec + add_nsec) / 1000000000);
	tv_nsec = (tv_nsec + add_nsec) % 1000000000;
	//tv_sec += (int)(add_time);
	//tv_nsec += (int)(add_time-((add_time) * 1000000000));
	return Py_BuildValue("ii", tv_sec, tv_nsec);
}


static PyObject *
rtplib_conv_timestamp_to_time(PyObject *self, PyObject *args){

    double timestamp, tv_sec, tv_nsec;
    if (!PyArg_ParseTuple(args, "f", &timestamp))
	        return NULL;
	tv_sec = (double)((long)(timestamp));
	tv_nsec = (int)(1000000000*(timestamp-tv_sec));
	return Py_BuildValue("ii", tv_sec, tv_nsec);
}


static PyObject *
rtplib_conv_time_to_timestamp(PyObject *self, PyObject *args){

    double timestamp;
    int tv_sec, tv_nsec;
    if (!PyArg_ParseTuple(args, "ii", &tv_sec, &tv_nsec))
	        return NULL;
	timestamp = (double)(tv_sec) + (double)(tv_nsec) / 1000000000;
	return Py_BuildValue("f", timestamp);
}


static PyObject *
rtplib_is_expired(PyObject *self, PyObject *args){
    /*
        Get time system for python
    */
    struct timespec time, current_time;
    if (!PyArg_ParseTuple(args, "ii", &time.tv_sec, &time.tv_nsec)) // Get time from python
	        return NULL;
	clock_gettime(CLOCK_REALTIME, &current_time);
	if (current_time.tv_sec == time.tv_sec){
	    if (current_time.tv_nsec > time.tv_nsec){
	        return Py_BuildValue("i", 1); // True
	    }else{
	        return Py_BuildValue("i", 0); // False
	    }
	}else if(current_time.tv_sec > time.tv_sec){
	    return Py_BuildValue("i", 1); // True
	}else{
	    return Py_BuildValue("i", 0); // False
	}
}


static PyObject *
rtplib_accuracy_dt(PyObject *self, PyObject *args){
    int reach_acc;
    int accuracy;
    int dt = -1;
    int q_size = -1;
    int max;
    int min;
    int sum;
    int current = 0;
    int i = 1;
    PyObject * queue;
    if (!PyArg_ParseTuple(args, "iO!", &reach_acc, &PyTuple_Type, &queue)) // Get time from python
	        return NULL;
	q_size = (int)PyTuple_Size(queue);
	if (q_size < 3)
	        return Py_BuildValue("iii", 0, -1, 0); // Error
	max = (int)(PyInt_AS_LONG(PyTuple_GET_ITEM(queue, 1)));
	min = max;
	sum = max;
    for (i=1; i<q_size; i++){
        current = (int)(PyInt_AS_LONG(PyTuple_GET_ITEM(queue, i)));
        sum = sum + current;
        max = fmax(max, current);
        min = fmin(min, current);
    }
    accuracy = max - min;
    if (accuracy <= reach_acc){
        dt = (int)((double)(sum) / q_size);
        return Py_BuildValue("iii", 1, dt, accuracy);
    }else{
        return Py_BuildValue("iii", 0, dt, accuracy);
    }
}



//static PyObject *
//rtplib_diff_time(PyObject *self, PyObject *args){
//    /*
//        Get time system for python
//    */
//    struct timespec time_a, time_b;
//    if (!PyArg_ParseTuple(args, "iiii", &time_a.tv_sec, &time_a.tv_nsec, &time_b.tv_sec, &time_b.tv_nsec)) // Get time from python
//	        return NULL;
//
//}

//static PyObject *
//rtplib_perform_sync(PyObject *self, PyObject *args){
//    /*
//        Perform a sync
//           :param s: ip
//           :param i: port
//           :param
//    */
//
//	if (!PyArg_ParseTuple(args, "sif", &time.tv_sec, &time.tv_nsec)) // Get time from python
//	        return NULL;
//	return Py_BuildValue("i", clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &time, &remain));
//}


static PyObject *
rtplib_wait_abs_time(PyObject *self, PyObject *args){
    /*
        Wait absolute time, then return
    */
    struct timespec time, remain;
	if (!PyArg_ParseTuple(args, "ii", &time.tv_sec, &time.tv_nsec)) // Get time from python
	        return NULL;
	return Py_BuildValue("i", clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &time, &remain));
}

static PyMethodDef RtplibMethods[] = {

    {"get_time",  rtplib_get_time, METH_VARARGS,
     "Get time system for python"},
    {"set_time",  rtplib_set_time, METH_VARARGS,
     "Set time system from python"},
    {"wait_abs_time",  rtplib_wait_abs_time, METH_VARARGS,
     "Wait absolute time, then return"},
    {"conv_timestamp_to_time",  rtplib_conv_timestamp_to_time, METH_VARARGS,
     "Convert python timestamp to (tv_sec, tv_nsec) "},
    {"conv_time_to_timestamp",  rtplib_conv_time_to_timestamp, METH_VARARGS,
     "Convert (tv_sec, tv_nsec) to python timestamp "},
    {"is_expired",  rtplib_is_expired, METH_VARARGS,
     "Return true if time is behind current_system_time"},
    {"remain_time",  rtplib_remain_time, METH_VARARGS,
     "Return the remaining time between time and current time"},
    {"add_time",  rtplib_add_time, METH_VARARGS,
     "Add float time to a given time (sec, nsec)"},
    {"accuracy_dt",  rtplib_accuracy_dt, METH_VARARGS,
     "Return accuracy and dt from reach accuracy and dt stack"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initrtplib(void)
{
    srand(time(NULL));
    (void) Py_InitModule("rtplib", RtplibMethods);
}