From your aws ecr describe-images output for the tts-backend repository, here’s a quick summary of the key points:
Latest Tagged Image:
sha256:8ff3f96bdc4a35d9143ac260a549e8736331273012354c49296bf49fdc49d5fe
Tagged as latest
Pushed: 2025-09-20T20:03:35-05:00
Size: ~119 MB
Manifest type: application/vnd.oci.image.index.v1+json
Other Significant Digests:
sha256:da2ec8b32db6cb950a6d26fb78ed4016bcdeec930ad8b2199267ff582ff0561e – Same size as latest (~119 MB), pushed the same time, could be another version or untagged duplicate.
Several smaller images (~1–1.3 KB) represent manifest/config references rather than full images.
Old Images:
Multiple images around ~98 MB pushed on 2025-08-31.
These seem like older builds; some have been pulled recently (lastRecordedPullTime).
Recommendation:
If you want to clean up the repository, you could consider retaining only latest and a few previous stable images and removing older untagged images.
The imageSizeInBytes shows which images are actual Docker layers vs just config/manifest metadata.
If you want, I can provide a one-liner AWS CLI command to delete all untagged or older images safely to free up space. Do you want me to do that?