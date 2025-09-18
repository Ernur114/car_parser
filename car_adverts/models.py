from django.db import models


class City(models.Model):
    title = models.CharField(verbose_name="название города", unique=True)
    alias = models.CharField(verbose_name="url параметр", default="")

    class Meta:
        ordering = ("id",)
        verbose_name = "город"
        verbose_name_plural = "города"


class Advert(models.Model):
    price = models.PositiveBigIntegerField(
        verbose_name="цена", null=True, blank=True
    )
    description = models.TextField(
        verbose_name="описание", null=True, blank=True
    )
    title = models.CharField(
        verbose_name="название", max_length=200, null=True, blank=True
    )
    year_of_issue = models.PositiveIntegerField(
        verbose_name="год выпуска", null=True, blank=True
    )
    characteristics = models.JSONField(
        verbose_name="характеристики", null=True, blank=True
    )
    city = models.ForeignKey(
        to=City,
        on_delete=models.CASCADE,
        related_name="city_adverts",
        verbose_name="город",
    )
    publication_date = models.DateField(
        verbose_name="дата публикации", null=True, blank=True
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "объявление"
        verbose_name_plural = "объявления"

    def __str__(self):
        return f"{self.title} -> {self.year_of_issue} -> {self.city}"


class AdvertImage(models.Model):
    image = models.ImageField(
        upload_to="advert_images", verbose_name="изображение"
    )
    advert = models.ForeignKey(
        to=Advert,
        on_delete=models.CASCADE,
        related_name="advert_images",
        verbose_name="объявление",
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "изображение"
        verbose_name_plural = "изображения"

    def __str__(self):
        return f"{self.pk} -> {self.advert}"
