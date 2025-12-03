from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone
from .models import Task
from .forms import TaskForm

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64
from collections import Counter
from datetime import datetime

def index(request):
    tasks = Task.objects.all().order_by("-id")
    form = TaskForm()
    return render(request, "todo_app/index.html", {"tasks": tasks, "form": form})

def add_task(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    form = TaskForm(request.POST)
    if form.is_valid():
        form.save()
    return redirect("home")

def edit_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = TaskForm(instance=task)
    return render(request, "todo_app/edit.html", {"form": form, "task": task})

def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        task.delete()
    return redirect("home")

def toggle_done(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.done:
        task.done = False
        task.completed_at = None
    else:
        task.done = True
        task.completed_at = timezone.now()
    task.save()
    return redirect("home")

def plot_done_by_day(request):
    # собираем даты в строковом формате YYYY-MM-DD по completed_at
    qs = Task.objects.filter(done=True, completed_at__isnull=False)
    days = [t.completed_at.astimezone(timezone.get_current_timezone()).date() for t in qs]
    cnt = Counter(days)
    if not cnt:
        # простой пиксель с текстом (или можно вернуть пустой 1x1)
        fig, ax = plt.subplots(figsize=(4,2))
        ax.text(0.5, 0.5, "No completed tasks", ha="center", va="center")
        ax.axis("off")
    else:
        xs = sorted(cnt.keys())
        ys = [cnt[d] for d in xs]
        fig, ax = plt.subplots(figsize=(6,2.5))
        # не задаём цвета явно
        ax.bar([d.strftime("%Y-%m-%d") for d in xs], ys)
        ax.set_title("Completed tasks by day")
        ax.set_xlabel("Day")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.getvalue(), content_type="image/png")
