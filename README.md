# Compreno2UD
A Compreno2UD converter to convert the original Compreno annotation trees into the Enhanced CoBaLD representation. Please cite

```
@inproceedings{petrova2024cobald,
title={CoBaLD Annotation: the Enrichment of the Enhanced Universal Dependencies with the Semantical Pattern},
author={Petrova, Maria and Ivoylova, Alexandra and Tishchenkova, Anastasia},
booktitle={Proceedings of the the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation},
year={2024}
}
```

## Conversion process

The converter takes a Compreno produced output in .json format, then the syntax annotation is being converted first to E-UD, then to base UD; finally, the syntactically conversed json is passed on to the morphological conversion and re-tokenization module. We have to create a temporary json output in order to be able to work on the syntax and morphology modules separately. 

## Testing and bugs

We also publish an .ipynb notebook with tests for the resulting .conllu file.
