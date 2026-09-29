# Pipeline Version 2 (Two Contributions)

> Quoted from DreamBooth (Ruiz et al., CVPR 2023): reuse the logic, not the wording. Its em dash ("magic photo booth”—once ...") breaks Writing Rule B3.7 in `SKILL.md`; use a colon or a new sentence instead.


`Version 2: Two contributions, and one teaser figure to present the basic idea.`

```latex
% In this paper, we propose a novel framework …
%% Example: In this work, we present a new approach for “personalization” of text-to-image diffusion models (adapting them to user-specific image generation needs).
In this paper, we propose a novel framework/representation, named [method name] for [xxx task].

% One-sentence key novelty
%% Example: More formally, given a few images of a subject (∼3-5), our objective is to implant the subject into the output domain of the model such that it can be synthesized with a unique identifier. To that end, we propose a technique to represent a given subject with rare token identifiers and fine-tune a pre-trained, diffusion-based text-to-image framework.
Our innovation is in [one sentence for key novelty].

% Teaser
%% Example: The effect is akin to a “magic photo booth”—once a few images of the subject are taken, the booth generates photos of the subject in different conditions and scenes, as guided by simple and intuitive text prompts (Figure 1).
The basic idea is illustrated in [xxx Figure].

% Contribution 1 details
%% Example: We fine-tune the text-to-image model with the input images and text prompts containing a unique identifier followed by the class name of the subject (e.g., “A [V] dog”).
Specifically, [how contribution 1 works].

% Advantage of contribution 1
%% Example: The latter enables the model to use its prior knowledge on the subject class while the class-specific instance is bound with the unique identifier.
In contrast to previous methods, [advantage of contribution 1].

% Challenge motivating contribution 2
%% Example: In order to prevent language drift [34, 40] that causes the model to associate the class name (e.g., “dog”) with the specific instance,
However, [another technical challenge].

% Contribution 2 details
%% Example: we propose an autogenous, class-specific prior preservation loss, which leverages the semantic prior on the class that is embedded in the model, and encourages it to generate diverse instances of the same class as our subject.
Specifically, [how contribution 2 works].
```
