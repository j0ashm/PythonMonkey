#include "include/modules/bifrost2/bifrost2.hh"

#include "include/StrType.hh"

#include <jsapi.h>
#include <js/CompilationAndEvaluation.h>
#include <js/Initialization.h>
#include <js/SourceText.h>

#include <Python.h>

static JSContext *cx;             /**< pointer to Bifrost's JSContext */
static JS::RootedObject *global;  /**< pointer to the global object of Bifrost's JSContext */

static void cleanup() {
  JS_DestroyContext(cx);
  JS_ShutDown();
  delete global;
}

static PyObject *eval(PyObject *self, PyObject *args) {

  StrType *code = new StrType(PyTuple_GetItem(args, 0));

  JSAutoRealm ar(cx, *global);
  JS::CompileOptions options (cx);
  options.setFileAndLine("noname", 1);

  JS::SourceText<mozilla::Utf8Unit> source;
  if (!source.init(cx, code->getValue(), strlen(code->getValue()), JS::SourceOwnership::Borrowed)) {
    PyErr_SetString(PyExc_RuntimeError, "Spidermonkey could not initialize with given JS code.");
    return NULL;
  }

  JS::RootedValue rval(cx);
  if (!JS::Evaluate(cx, options, source, &rval)) {
    PyErr_SetString(PyExc_RuntimeError, "Spidermonkey could not evaluate the given JS code.");
    return NULL;
  }

  Py_RETURN_NONE;
}

static PyMethodDef Bifrost2Methods[] = {
  {"eval", eval, METH_VARARGS, "Javascript evaluator in Python"},
  {NULL, NULL, 0, NULL}
};

static struct PyModuleDef bifrost2 =
{
  PyModuleDef_HEAD_INIT,
  "bifrost2",                                   /* name of module */
  "A module for python to JS interoperability", /* module documentation, may be NULL */
  -1,                                           /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
  Bifrost2Methods
};

PyMODINIT_FUNC PyInit_bifrost2(void)
{
  if (!JS_Init())
    return NULL;

  cx = JS_NewContext(JS::DefaultHeapMaxBytes);
  if (!cx)
    return NULL;

  if (!JS::InitSelfHostedCode(cx))
    return NULL;

  JS::RealmOptions options;
  static JSClass globalClass = {"global", JSCLASS_GLOBAL_FLAGS, &JS::DefaultGlobalClassOps};
  global = new JS::RootedObject(cx, JS_NewGlobalObject(cx, &globalClass, nullptr, JS::FireOnNewGlobalHook, options));
  if (!global)
    return NULL;

  Py_AtExit(cleanup);
  return PyModule_Create(&bifrost2);
}