from django.core.exceptions import ValidationError
from django.forms import BooleanField, ModelForm

from publications.models import Post

FORBIDDEN_WORDS = [
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
    "реклама",
]


class StyleFormMixin:
    """Стилизация форм"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label


class PostForm(StyleFormMixin, ModelForm):
    """Форма для модели Post"""

    class Meta:
        model = Post
        fields = ["name", "title", "image", "content"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name", "").lower()
        content = cleaned_data.get("content", "").lower()
        for word in FORBIDDEN_WORDS:
            if word in name or word in content:
                raise ValidationError(f"Недопустимое слово: {word}")
        return cleaned_data
