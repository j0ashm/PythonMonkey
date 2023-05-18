/**
 * @file internalBinding.hh
 * @author Tom Tang (xmader@distributive.network)
 * @brief
 * @version 0.1
 * @date 2023-05-16
 *
 * @copyright Copyright (c) 2023 Distributive Corp.
 *
 */

#include <jsapi.h>
#include <Python.h>

JSObject *createTimersInternalBinding(JSContext *cx);
// JSObject *createXXXInternalBinding(JSContext *cx);

JSObject *getInternalBindingsByNamespace(JSContext *cx, JSLinearString *namespaceStr);

PyObject *getInternalBindingPyFn(JSContext *cx);