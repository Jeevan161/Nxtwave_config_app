from django.shortcuts import render
from django.db.models import Count, Sum
from django.utils.timezone import now, timedelta
from models.models import ResourceLoadData


def content_dashboard(request):
    # Define resource types (ensure they match the values in your model)
    resource_types = ['TUTORIAL', 'MCQ PRACTICE', 'CODING PRACTICE']

    # Get today's date and the start of the week
    today = now().date()
    week_start = today - timedelta(days=today.weekday())

    def get_stats(queryset):
        # Calculate for each resource_type
        result = []
        for rtype in resource_types:
            qs_rtype = queryset.filter(resource_type=rtype)
            created_count = qs_rtype.count()
            total_updates = qs_rtype.aggregate(s=Sum('updated_count'))['s'] or 0
            total_questions = qs_rtype.aggregate(s=Sum('no_question'))['s'] or 0

            result.append({
                'resource_type': rtype,
                'created_count': created_count,
                'total_updates': total_updates,
                'total_questions': total_questions,
            })
        return result

    # Query sets
    today_qs = ResourceLoadData.objects.filter(time_loaded__date=today)
    weekly_qs = ResourceLoadData.objects.filter(time_loaded__date__gte=week_start, time_loaded__date__lte=today)
    total_qs = ResourceLoadData.objects.all()

    # Stats lists
    today_stats = get_stats(today_qs)
    weekly_stats = get_stats(weekly_qs)
    total_stats = get_stats(total_qs)

    # Pre-calculate totals
    total_resources = sum(stat['created_count'] for stat in total_stats)
    today_updates = sum(stat['total_updates'] for stat in today_stats)
    total_questions = sum(stat['total_questions'] for stat in total_stats)
    stats_data = [
        ("Today's Statistics", today_stats, "blue", "Today"),
        ("Weekly Statistics", weekly_stats, "green", "Weekly"),
        ("Total Statistics", total_stats, "purple", "Total")
    ]
    context = {
        'today_stats': today_stats,
        'weekly_stats': weekly_stats,
        'total_stats': total_stats,
        'total_resources': total_resources,
        'today_updates': today_updates,
        'total_questions': total_questions,
        'stats_data': stats_data,
    }
    return render(request, 'Beta/content-dashboard.html', context)