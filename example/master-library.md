## Build a Slide Library

Instead of creating slides from scratch each time, build a **Master library** and assemble presentations by **cloning**.

```
Presentations
  Master              ← your slide library
    Topic A
      Slide - Intro to A
      Slide - A Deep Dive
    Topic B
      Slide - B Overview
  Sets                ← finished presentations
    Workshop Beginners
      Title           ← unique (from template)
      Intro to A      ← cloned from Master
      B Overview      ← cloned from Master
    Workshop Advanced
      Title           ← unique
      A Deep Dive     ← cloned from Master
```

::: {.notes}
The Master area is organized by topic, not by presentation. Sets are the actual presentations — assembled from clones.
:::