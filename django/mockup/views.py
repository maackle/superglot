from django.views.generic import TemplateView

class HomeView(TemplateView):
	template_name = 'mockup/index.jade'


class AnyJadeView(TemplateView):

	def dispatch(self, request, *args, **kwargs):
		self.template_name = 'mockup/' + kwargs['template_name'] + '.jade'
		return super(AnyJadeView, self).dispatch(request, *args, **kwargs)