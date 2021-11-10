# Overview

This interface layer handles communication with MySQL via the `mysql-monitor`
interface protocol.


# Usage

The `mysql-monitor` interface is meant to be used with granted `SELECT` and
`SHOW VIEW` privileges to every database and table for a MySQL user. This mean
that user will have only read access and could collect all metrics. 

## Requires

## Provides