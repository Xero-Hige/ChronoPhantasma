# ChronoPhantasma
## Solving the load balancing problem in distributed systems with Game Theory and Genetic Algorithm

Class project for Algorithms: Design & Analysis II

## Simulator

### Running a simulation

The simulator requires Python 3.5 or greater and matplotlib installed. To start the simulation:
`python3 <struct_file> [<seconds to simulate> [<output graph file>]]`

### Struct File

```json
{
  "machines_times": [<machine0 time>, ... , <machinei time>],
  "clients": [
    {
      "lambda": <client0 lambda>,
      "allocation": [<fraction of job to machine0>, ... , <fraction of job to machinei>]
    }, {
   ...
      "lambda": <clientn lambda>,
      "allocation": [<fraction of job to machine0>, ... , <fraction of job to machinei>]
    }
}
```

### Demo
Demo of the project working can be found [here](https://github.com/Xero-Hige/ChronoPhantasma/blob/master/Presentacion.ipynb).

