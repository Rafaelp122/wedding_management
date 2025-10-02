from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .forms import ItemForm
from apps.users.models import Planner
from apps.weddings.models import Wedding
from apps.items.models import Item

@login_required
def partial_items(request, wedding_id):
    planner = get_object_or_404(Planner, user=request.user)
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
    items = Item.objects.filter(wedding=wedding).select_related('supplier')
    context = {"wedding": wedding, "items": items}
    return render(request, "items/items_partial.html", context)


@login_required
def add_item(request, wedding_id):
    planner = get_object_or_404(Planner, user=request.user)
    wedding = get_object_or_404(Wedding, id=wedding_id, planner=planner)
    
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.wedding = wedding
            item.save()
            return partial_items(request, wedding_id) 
    else: 
        form = ItemForm()
        
    return render(request, 'items/partials/add_item_form.html', {'form': form, 'wedding': wedding})