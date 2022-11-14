# Inventory

[![Build Status](https://github.com/CSCI-GA-2820-FA22-001/inventory/actions/workflows/tdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-FA22-001/inventory/actions)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-FA22-001/inventory/branch/master/graph/badge.svg?token=671PK2KTUM)](https://codecov.io/gh/CSCI-GA-2820-FA22-001/inventory)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

This repository contains the work done by the Inventory Squad as a part of DevOps course in Fall '22 by John Rofrano.

## Description

The inventory resource keeps track of how many of each products we have in our warehouse.
At a minimum it should reference a product and the quantity on hand. Inventory should also
track restock levels and the condition of the item (i.e., new, open box, used) as an enumeration.
Restock levels will help you know when to order more products. Being able to query products by
their condition (e.g., new, used) could be very useful. A good action for the inventory API is to be able to activate and deactivate an inventory item.

## Squad Members
|Name                              |NYU netID         |
|----------------------------------|---------------|
|[Arpan Ghoshal](https://github.com/arpanghoshal)                     | ag8821@nyu.edu|
|[Qiyuan Huang](https://github.com/cookythecat)                      | qh2086@nyu.edu|
|[Shantanu Mahapatra](https://github.com/santa-mota)                | sm9243@nyu.edu|
|[Swapnil Gupta](https://github.com/500swapnil)                     | sg6665@nyu.edu|
|[Nava Hirschorn](https://github.com/Nava-Hirschorn)                    | nh2144@nyu.edu|

## API Endpoints
_TODO_

## How to run and test locally

```bash
git clone git@github.com:DevOps-Fall2022-Inventory/inventory.git
## To run, open in VSCode and run it in a docker container
## In the docker container, to launch the app on local server:
honcho start
## To run tests
nosetests
```
