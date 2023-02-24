/**
 * @file NoneType.hh
 * @author Caleb Aikens (caleb@distributive.network)
 * @brief Struct for representing None
 * @version 0.1
 * @date 2023-02-22
 *
 * @copyright Copyright (c) 2023
 *
 */

#ifndef PythonMonkey_NoneType_
#define PythonMonkey_NoneType_

#include "PyType.hh"
#include "TypeEnum.hh"

#include <iostream>

/**
 * @brief This struct represents the 'None' type in Python. It inherits from the PyType struct
 */
struct NoneType : public PyType {
public:
  NoneType();
  const TYPE returnType = TYPE::NONE;

protected:
  virtual void print(std::ostream &os) const override;
};

#endif