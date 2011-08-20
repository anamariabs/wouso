from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

def validate_dynq_code():
    # TODO: code should be validate here so we don't break the site
    # by executing bad code
    pass

class Tag(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name

class Question(models.Model):
    text = models.TextField()
    proposed_by = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_proposedby_related")
    endorsed_by = models.ForeignKey(User, null=True, blank=True, related_name="%(app_label)s_%(class)s_endorsedby_related")
    active = models.BooleanField(default=False)

    tags = models.ManyToManyField(Tag, blank=True, related_name="%(app_label)s_%(class)s_related")
    answer_type = models.CharField(max_length=1, choices=(("R", "single choice"), ("C", "multiple choice")), default="R")
    # a dynamic question would have its code run before returning it to the caller
    type = models.CharField(max_length=1, choices=(("S", "static"), ("D", "dynamic")), default="S")
    code = models.TextField(blank=True, validators=[validate_dynq_code], 
                            help_text="Use %text for initial text, %user for the user that sees the question.")

    @property
    def answers(self):
        try:
            return Answer.objects.filter(question=self).all()
        except Answer.DoesNotExist:
            return None
        
    @property
    def day(self):
        try:
            return Schedule.objects.filter(question=self)[0].day
        except (Schedule.DoesNotExist, IndexError):
            return None

    def is_valid(self):
        if self.answers.count() == 0:
            return False
        if self.answers.filter(correct=True).count() == 0:
            return False
        return True
    
    def add_tag(self, tag):
        if not isinstance(tag, Tag):
            tag = Tag.objects.create(name=tag)
            tag.save()
        return self.tags.add(tag)
        
    def has_tag(self, tag):
        if not isinstance(tag, Tag):
          try:
              tag = Tag.objects.get(name=tag)
          except Tag.DoesNotExist:
              return False
        return tag in self.tags.all()
    
    @property
    def question(self):
        return unicode(self.text)
    
    def tag(self):
        tlist = self.tags.all()
        ret = ""
        
        # no tags assigned to the question
        if not tlist:
            return ''
                
        for t in tlist:
            ret += str(t) + ", "
            
        return ret[:-2]
        
    def scheduled(self):
        slist = Schedule.objects.filter(question=self)
        ret = ""
        
        # no days scheduled for the question
        if not slist:
            return ''
                
        for s in slist:
            ret += str(s) + ", "
            
        return ret[:-2]
    
    def __unicode__(self):        
        return unicode(self.text)
    
class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="zanswers")
    text = models.TextField()
    explanation = models.TextField(null=True, default='', blank=True)
    correct = models.BooleanField()
    
    def __unicode__(self):
        return self.text
        
class Schedule(models.Model):
    question = models.ForeignKey(Question, related_name="schedule")
    day = models.DateField(default=datetime.now, blank=True)

    def __unicode__(self):
        return str(self.day)