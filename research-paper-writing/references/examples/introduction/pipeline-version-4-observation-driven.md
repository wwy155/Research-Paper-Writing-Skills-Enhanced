# Pipeline Version 4 (Observation-Driven Contribution)

> Quoted from LoRA (Hu et al., ICLR 2022): reuse the logic, not the wording. Its trailing participles (", leading to our proposed ...", ", making LoRA ...", ", reducing ...", ", introducing ...") break Writing Rule B3.1 in `SKILL.md`; state each consequence as its own sentence.


`Version 4: Contribution comes from one important observation. Introduce key innovation first, then intuitive observation as motivation, then method details, then benefits.`

```latex
% Observation as motivation, and the key innovation it leads to
% (LoRA states the observation first and names the method in the same sentence; either order works when both come within the first two sentences.)
%% Example: We take inspiration from Li et al. (2018a); Aghajanyan et al. (2020) which show that the learned over-parametrized models in fact reside on a low intrinsic dimension. We hypothesize that the change in weights during model adaptation also has a low “intrinsic rank”, leading to our proposed Low-Rank Adaptation (LoRA) approach.
Our innovation is [one sentence for key novelty]. We observe that [observation].

% Method details
%% Example: LoRA allows us to train some dense layers in a neural network indirectly by optimizing rank decomposition matrices of the dense layers’ change during adaptation instead, while keeping the pre-trained weights frozen, as shown in Figure 1.
Considering that [observation], we [how the method works], as shown in [xxx Figure].

% Evidence that the observation holds
%% Example: Using GPT-3 175B as an example, we show that a very low rank (i.e., r in Figure 1 can be one or two) suffices even when the full rank (i.e., d) is as high as 12,288, making LoRA both storage- and compute-efficient.
[Evidence, with numbers, that the observation holds.]

% Benefits
%% Example: LoRA possesses several key advantages.
%% Example: A pre-trained model can be shared and used to build many small LoRA modules for different tasks. We can freeze the shared model and efficiently switch tasks by replacing the matrices A and B in Figure 1, reducing the storage requirement and task-switching overhead significantly.
%% Example: Our simple linear design allows us to merge the trainable matrices with the frozen weights when deployed, introducing no inference latency compared to a fully fine-tuned model, by construction.
This leads to [benefit] and achieves [result].
```
