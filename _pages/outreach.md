---
title: "Outreach"
layout: single
permalink: /outreach/
---

# Press Releases

{% for post in site.outreach reversed %}

## {{ post.title }}

{% if post.image %}
<figure>
  <img src="{{ post.image }}" alt="{{ post.title }}">
  {% if post.image_credit %}
  <figcaption><em>Credit: {{ post.image_credit }}</em></figcaption>
  {% endif %}
</figure>
{% endif %}

**Published:** {{ post.date | date: "%B %Y" }}  
**Journal:** {{ post.journal }}

{{ post.excerpt }}

{% for link in post.links %}
- [{{ link.label }}]({{ link.url }})
{% endfor %}

---

{% endfor %}
