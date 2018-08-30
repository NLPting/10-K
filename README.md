# NER


Windows :

import io
def load_from_file(cls, model_file):
with open(model_file,'rb') as f:
  buffer = io.BytesIO(f.read())
  state = torch.load(buffer, map_location={'cuda:0': 'cpu'})
