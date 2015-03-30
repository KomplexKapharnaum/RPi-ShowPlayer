#include <Python.h>
#include <time.h>
//#include <stdlib.h>
//#include <stdio.h>


static PyObject *
acklib_gen_uids(PyObject *self, PyObject *args){
    /*
        Generate uids from the ACK port, see README for details
    */
    struct timespec time;
    clock_gettime(CLOCK_REALTIME, &time);
    //printf("clock, sec : %d , nsec : %d", time.tv_sec, time.tv_nsec);
	int i_time = (int)((0xFFFF0000 & time.tv_sec) | ((0xFFFF0000 & time.tv_nsec) >> 16));
	int p = (int)(rand());
	return Py_BuildValue("ii", i_time, p);
}

//static PyObject *
//acklib_encode_uid(PyObject *self, PyObject *args){
//    /*
//        This function encode the complete uid in two integers in order to be transport by OSC
//    */
//	long uid;
//	if (!PyArg_ParseTuple(args, "l", &uid)) // Get the port number from python
//	        return NULL;
//	return Py_BuildValue("ii", ((0xFFFFFFFF00000000 & uid) >> 32), (0x00000000FFFFFFFF & uid));
//}
//
//static PyObject *
//acklib_decode_uids(PyObject *self, PyObject *args){
//    /*
//        Decode uids to get an unique ID based on time and random, and the port number to answer
//        :param uidt:
//        :param uidp:
//        :return: uid, port
//    */
//	long uidt, uidp;
//	if (!PyArg_ParseTuple(args, "ll", &uidt, &uidp)) // Get the port number from python
//	        return NULL;
//	return Py_BuildValue("ii", (uidp | (uidt << 32)), (0x0000FFFF & uidp));
//}

static PyMethodDef AcklibMethods[] = {

    {"gen_uids",  acklib_gen_uids, METH_VARARGS,
     "Generate uids from the ACK port, see README for details"},
//    {"encode_uid",  acklib_encode_uid, METH_VARARGS,
//     "This function encode the complete uid in two integers in order to be transport by OSC"},
//    {"decode_uids",  acklib_decode_uids, METH_VARARGS,
//     "Decode uids to get an unique ID based on time and random, and the port number to answer"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initacklib(void)
{
    srand(time(NULL));
    (void) Py_InitModule("acklib", AcklibMethods);
}