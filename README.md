# dexcov

Tool for generating a [Dextool Mutate](https://github.com/joakim-brannstrom/dextool/tree/master/plugin/mutate) vs [LCOV](https://github.com/linux-test-project/lcov) side by side presentation

Example:

```
$ dexcov example/lcov_html example/dextool_html -o example/out
$ xdg-open example/out/lz4.c.html
```

![pic1](https://i.imgur.com/dPqurbl.png)
