# cd mob_dataset
# tdfs build
import tensorflow_datasets as tfds
from pathlib import Path

class MobDataset(tfds.core.GeneratorBasedBuilder):
    VERSION = tfds.core.Version('1.0.12')
    RELEASE_NOTES = {
      '1.0.0': 'Initial release.',
      '1.0.1': 'Dataset added',
        '1.0.11': 'bug fixed (dataset mask directory fixed)',
        '1.0.12': 'added more data in dataset(60-2)'
    }
    def _info(self) -> tfds.core.DatasetInfo:
        return tfds.core.DatasetInfo(
            builder=self,
            features=tfds.features.FeaturesDict({
                'image': tfds.features.Image(shape=(None, None, 3)),
                'mask':  tfds.features.Text(),
            }),
            supervised_keys=('image', 'mask'),
        )
    def _split_generators(self, dl_manager: tfds.download.DownloadManager):
        path = Path("Dataset")
        return {
            'train': self._generate_examples(path / 'train'),
            'test': self._generate_examples(path / 'test'),
        }
    def _generate_examples(self, path):
        for f in path.glob('img/*.png'):
            yield f.name, {
              'image': f,
              'mask': str(path / Path(f"mask/mask_{str(f.stem)}")),
            }
