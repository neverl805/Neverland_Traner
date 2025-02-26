import os
from PIL import Image
import open_clip
import torch

# pip install open_clip_torch

device = "cuda" if torch.cuda.is_available() else "cpu"
# device = "cuda"
def load_clip_model(download_dir=None):
    if download_dir != None:
        os.environ['TORCH_HOME'] = download_dir
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-B-16',
                 pretrained = 'laion2b_s34b_b88k',
                 device=device,
                 )
    tokenizer = open_clip.get_tokenizer('ViT-B-16')
    return model, tokenizer, preprocess


def clip_predict(image_path,token_list,model, tokenizer, preprocess):

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)
    text = tokenizer(token_list).to(device)

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)
        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        text_probs = (100.0 * image_features @ text_features.T).softmax(dim=-1)
        max_prob, max_index = torch.max(text_probs, dim=1)
        max_prob = max_prob.item()
        max_index = max_index.item()

    return [(token_list[max_index],max_prob)]

if __name__ == '__main__':
    path = r"C:\Users\admin\Desktop\ssdd\half_model_label\840adb646f1352b10cef0ecde3135d3.png"
    model, tokenizer, preprocess = load_clip_model()
    result = clip_predict(path,["a diagram", "a dog", "drumstick"],model, tokenizer, preprocess)[0]
    print(result)
