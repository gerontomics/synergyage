from django import forms


class SubmitForm(forms.Form):
	# we make them required in Javascript, based on current tab
	pubmed = forms.IntegerField(required=False)
	citation = forms.CharField(max_length=500, required=False)
	email = forms.EmailField()
	description = forms.CharField(max_length=5000, widget=forms.Textarea)
	type = forms.IntegerField(initial=1, widget=forms.HiddenInput())
	pubmed.widget.attrs.update({'class': 'form-control', 'placeholder': 'PubMed ID'})
	citation.widget.attrs.update({'class': 'form-control', 'placeholder': 'Citation'})
	email.widget.attrs.update({'class': 'form-control', 'placeholder': 'Please enter your email address', })
	description.widget.attrs.update(
		{'class': 'form-control margin-top', 'rows': '3', 'placeholder': 'Reason for choosing this article'})
