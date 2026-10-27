---
title: "Outreach"
layout: single
permalink: /outreach/
---

# Press Releases

{% for post in site.outreach reversed %}

## {{ post.title }}

**Published:** {{ post.date | date: "%B %Y" }}  
**Journal:** {{ post.journal }}

{{ post.excerpt }}

{% for link in post.links %}
- [{{ link.label }}]({{ link.url }})
{% endfor %}

---

{% endfor %}
