# Average Prices of Fairness for Envy Cycle Elimination Heuristics

This repository contains the code used in the experiment for our paper, titled ["Optimizing the Envy Cycle Elimination Algorithm"](#CelineSu26).

[![arXiv](https://img.shields.io/badge/arXiv-2606.02233-b31b1b.svg)](https://arxiv.org/abs/2606.02233)

## Table of contents

* [Introduction](#introduction)
* [Quick start](#quick-start)
* [Usage](#usage)
  + [Types of distributions](#types-of-distributions)
  + [Real-world data: User instances](#real-world-data-user-instances)
  + [Synthetic data: Probabilistic distributions](#synthetic-data-probabilistic-distributions)
  + [Output files](#output-files)
  + [Testing](#testing)
  + [References](#references)

## Introduction
The *envy cycle elimination (ECE) algorithm* is a fundamental method in allocating indivisible goods, as it satisfies the prominent fairness notion of *envy-freeness up to one good (EF1)* [[Lipton et al., 2004]](#LiptonMaMo04).
The algorithm works by alternating between allocating an available good to an unenvied agent and resolving any existing envy cycle.
The resulting allocation satisfies EF1 regardless of the choices of available good and unenvied agent in each iteration.

In our paper [[Celine and Suksompong, 2026]](#CelineSu26), we investigated several natural heuristics for choosing an available good and/or an unenvied agent in each iteration of the ECE algorithm, and compared their worst-case efficiency loss using the *price of fairness* concept.
We also analyzed the average-case efficiency loss using experimental results.
The code contained in this repository was used in the implementation of the aforementioned experiment.
We refer the reader to our paper (or its [preprint](https://arxiv.org/abs/2606.02233) version) for more details on the model and definitions.


## Quick Start

Make sure [Python](https://pythongeeks.org/python-3-installation-and-setup-guide/) is installed.[^1]
Download the file [`ece_heuristics.py`](https://github.com/karen-celine/envy-cycle-elimination-heuristics/blob/main/ece_heuristics.py) and run it.

```
python ece_heuristics.py
```

[^1]: For the experiment, the code was run using Python version 3.10.1.


## Usage

### Types of distributions

The experiment can be conducted using real-world or synthetic data.
For the real-world data, the user can input custom instances according to the specified format.
For synthetic data, the program will generate sets of instances by sampling the utilities from uniform, exponential, and log-normal probabilistic distributions.

The user can choose which category (or categories) to run from the command-line argument when the following prompt appears:

```
Run the experiment with:
1) user instances only;
2) probabilistic distributions only;
3) both types of instance distributions.
Select an option (1/2/3):
```

### Real-world data: User instances

In our [paper](#CelineSu26), we conducted the experiment using data from [Spliddit](http://www.spliddit.org/).
The dataset is not included in this repository since it is not owned by us.
However, we allow the user to run the program using their own custom instances.

Some sample files for user instances is given in [`instances/sample/2-4.csv`](https://github.com/karen-celine/envy-cycle-elimination-heuristics/blob/main/instances/sample/2-4.csv) and [`instances/sample/3-3.csv`](https://github.com/karen-celine/envy-cycle-elimination-heuristics/blob/main/instances/sample/3-3.csv).

#### File name
Generally, the file name should folllow the format `n-m.csv` where `n` should be replaced with the number of agents and `m` should be replaced with the number of goods.
The code allows `n` to be either 2 or 3, and `m` to be between `n` and 9 (inclusive of the endpoints).
For any other values of `n` and `m`, edit lines [385](https://github.com/karen-celine/envy-cycle-elimination-heuristics/blob/cf990996fa458a1b3a80f06201850553ce6637fa/ece_heuristics.py#L385) and [386](https://github.com/karen-celine/envy-cycle-elimination-heuristics/blob/cf990996fa458a1b3a80f06201850553ce6637fa/ece_heuristics.py#L386) of the file `ece_heuristics.py` respectively.

#### Directory
The directory containing such files can be specified when the user is prompted by the program:

```
Enter directory containing user instances (e.g. "instances/sample"):
```

The program will read instances contained in the files in this directory.
If those files are placed in the same directory as the file `ece_heuristics.py`, leave this question blank and press `Enter`.

#### File format

The content of each CSV file must follow the required format. For example, the first two rows of the file [`instances/sample/2-4.csv`](https://github.com/karen-celine/envy-cycle-elimination-heuristics/blob/main/instances/sample/2-4.csv) are reproduced below:

```
instances
"[[0, 0, 1, 0], [0.5, 0.5, 0, 0]]"
```

The first line of the CSV file must contain the exact word `instances`.
Each subsequent line corresponds to an instance with $n$ agents and $m$ goods, represented by a list of $n$ inner lists, each of which contains $m$ numbers.
The $i$-th inner list describes the utility function of agent $i$, whereby the $j$-th item of this inner list corresponds to agent $i$'s utility for good $g_j$.

Note that each instance will be normalized such that each agent's utilities for all of the goods sum up to $1$.

### Synthetic data: Probabilistic distributions

Since real-world data may not be readily available, we also used synthetic data in our experiment, where the instances were generated using probabilistic distributions.
To run the experiment on probabilistic distributions, the file `ece_heuristics.py` is sufficient, and no additional dataset is required.

#### Random seed

We allow running the experiment with or without a random seed.
A seed is used to replicate the outcome exactly.
For example, the experimental results outlined in our [paper](#CelineSu26) can be reproduced exactly, using the published seed `ece`.

When the following prompt appears, type `y` to use a random seed; otherwise, type `n`.

```
Use seeded random number generator? (y/n)
```

If the answer to the previous question is `y`, the user will be prompted whether to use a custom seed, or use the default seed, which is `ece`.

```
Use custom seed? (y/n)
```

If the answer to the previous question is `y`, the user can then type their preferred seed, which can be any string.

```
Enter custom seed (any combination of letters, numbers, and symbols):
```

### Output files

All of the output files will be placed in the directory `output`.
If this directory is not empty, the user will be prompted whether to overwrite data.
This includes cases where the script `ece_heuristics.py` has been run at least once.

```
Directory "output/" is not empty.
Overwrite data? (y/n)
```

If the user inputs `n`, the program will be terminated, and the user may rerun the script after saving existing data to a separate location.

#### Detailed output

There are two types of output files.
First, for each tested distribution, $n$, and $m$, the program outputs a file named `distribution-n-m.csv`, where:
* `distribution` is replaced by the name of the distribution, which can be `user`, `random`, `exp`, or `lognorm`;
* `n` is the number of agents, which can be either 2 or 3; and
* `m` is the number of goods, which can be between `n` and 9, inclusive of both endpoints.

> Note: For user instances, if the file `n-m.csv` is not supplied for some values of `n` and `m`, the file `user-n-m.csv` will not be created and existing files named `user-n-m.csv` (which may have been created in previous executions of the script) will be removed.

This file lists each instance tested
(for experiments run using probabilistic distributions, the instances generated are not known prior to the experiment).
The file also includes for each instance:
* its maximum utilitarian welfare (MUW),
* its maximum egalitarian welfare (MEW), and
* for each ECE heuristic:
  + the allocation produced by the heuristic,
  + its utilitarian welfare, and
  + its egalitarian welfare.

For example, the first ten columns of the first two lines of the file `user-2-4.csv` (obtained from the user instances given in  [`instances/sample/2-4.csv`](https://github.com/karen-celine/envy-cycle-elimination-heuristics/blob/main/instances/sample/2-4.csv)) are given as a table below:

| | Instance | MUW | MEW | No heuristic | UW.0 | EW.0 | Agent with max util | UW.1 | EW.1 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | [[0.0, 0.0, 1.0, 0.0], [0.5, 0.5, 0.0, 0.0]] | 2.0 | 1.0 | [[0, 2, 3], [1]] | 1.5 | 0.5 | [[2, 3], [0, 1]] | 2.0 | 1.0 |

The allocation produced by each ECE heuristic is represented as a list of $n$ inner lists, where the $i$-th inner list contains the goods (indexed starting from `0`) allocated to agent $i$.

#### Summary file

The file named `summary.csv` aggregates the data for each distribution, $n$, and $m$, by providing the average utilitarian or egalitarian price for each heuristic.
For example, the table below shows the first six columns of the first two lines of the file `summary.csv`.

| | Distribution | n | m | UP-No heuristic | UP-Agent with max util | 
|---|---|---|---|---|---|
| 0 | user | 2 | 4 | 1.4594591307519456 | 1.1612900770027994 | 


### Testing

For the actual experiment, we used 10,000 instances for each probabilistic distribution, number of agents $n$, and number of goods $m$.
While the large sample size helps to improve precision, it took roughly 3 hours to complete the experiment.
For practicality, we allow the experiment to be run using fewer instances.

```
Run a smaller version of the experiment? (y/n)
```

If the answer to the above question is `y`, the user will then be prompted to enter a maximum number of instances for each set of parameters (distribution, $n$, and $m$).
Otherwise, for probabilistic distributions, 10,000 instances will be generated for each set of parameters, whereas for user instances, the experiment will be run using all instances provided.

```
Enter maximum number of instances for each distribution (1-10000):
```

The input must be an integer between 1 and 10,000 including both endpoints, without typing any commas (e.g. type `1000` instead of `1,000`).

## References
<a id="LiptonMaMo04">Richard J. Lipton, Evangelos Markakis, Elchanan Mossel, and Amin Saberi.</a>
On approximately fair allocations of indivisible goods.
In *Proceedings of the 5th ACM Conference on Electronic Commerce (EC)*, pages 125--131, 2004.

<a id="CelineSu26">Karen Frilya Celine and Warut Suksompong.</a>
Optimizing the envy cycle elimination algorithm.
In *Proceedings of the 40th Annual Conference on Neural Information Processing Systems (NeurIPS)*, Dec 2026. Forthcoming.