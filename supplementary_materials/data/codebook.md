# Coding Codebook

The final coding framework contains nine dimensions adapted from Apruzzese et
al.'s theory-practice gap framework.

## General Dimensions

`G1. Primary Contribution`

- `atk`: proposes a new attack method or technique.
- `def`: proposes a new defense, detection, or mitigation method.
- `both`: proposes both a novel attack and a novel defense.

`G2. Attack Category`

- `Evasion`: test-time adversarial examples or input perturbations.
- `Poisoning`: training-time attacks, backdoors, trojans, or data poisoning.
- `Privacy`: membership inference, model extraction, attribute inference, or related privacy leakage.
- `Multiple`: more than one attack category.
- `NA`: defense paper that does not focus on a specific attack type.

`G3. Data Modality`

- `Images`: vision tasks.
- `Text`: NLP, language model, or text classification tasks.
- `Audio`: speech or acoustic tasks.
- `Malware`: binary analysis, malware, network intrusion, or security telemetry.
- `Other`: tabular, graph, multimodal, reinforcement learning, federated learning, or other domains.

`G4. Economic Analysis`

- `Yes`: explicit monetary analysis, market pricing, itemized cost breakdown, ROI, or cost-benefit analysis with quantitative economic figures.
- `No`: technical metrics only, such as query counts, GPU-hours, runtime, perturbation budgets, or qualitative mentions of cost.

`G5. Code Availability`

- `Yes`: implementation code is publicly available.
- `No`: no public implementation code is mentioned.

`G6. Real-System Testing`

- `Yes`: evaluated on a deployed, production, commercial, or public API system.
- `No`: evaluated only on offline datasets, local models, simulations, benchmarks, or laboratory testbeds.

## Threat and Query Dimensions

`T1. Threat Model`

- `White-box`: full access to architecture, weights, gradients, or internals.
- `Gray-box`: partial access or surrogate knowledge.
- `Black-box`: query-only access without internal model access.
- `White-box/Black-box`: evaluates both white-box and black-box settings.
- `NA`: not structurally applicable.

`Q1. Gradient Dependency`

- `Yes`: method requires gradient computation through the target or defended model.
- `No`: gradient-free method.
- `NA`: gradient access is structurally irrelevant.

`Q2. Query Complexity`

- `High`: more than 1000 target-model queries.
- `Low`: 1 to 1000 target-model queries.
- `None`: no target-model queries required.
- `NA`: query count is not applicable to the method.

## Gap Score

The 0--5 Gap Score sums five binary indicators:

1. White-box or mixed white-box/black-box access.
2. Gradient dependency.
3. High query budget.
4. No real-system testing.
5. No strict economic analysis.

The score is descriptive, not a quality judgment of individual papers.
