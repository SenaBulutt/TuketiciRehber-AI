# RAG Test Sonuçları

Bu testler Microsoft Foundry Local RAG Asistanının retrieval,
cevap üretimi, kaynak kullanımı ve güvenli fallback davranışını
değerlendirmek amacıyla uygulanmıştır.

| # | Soru | Beklenen Davranış | Sonuç |
|---|---|---|---|
| 1 | Foundry Local nedir ve ne işe yarar? | İlgili Foundry Local dokümanını bulmalı ve cevap üretmeli | ✅ Başarılı |
| 2 | Embedding nedir ve RAG sisteminde ne işe yarar? | RAG/embedding dokümanını bulmalı | ✅ Başarılı - küçük model nedeniyle dil kalitesi sınırlı |
| 3 | Foundry Local hangi donanımlardan yararlanabilir? | İlgili SDK/donanım bilgisini bulmalı | ✅ Başarılı |
| 4 | Model kataloğu ne işe yarar? | Model Catalog kaynağını bulmalı | ✅ Başarılı |
| 5 | Foundry Local için Python sürümü ne olmalıdır? | Get Started kaynağından cevap vermeli | ✅ Başarılı |
| 6 | Türkiye'nin başkenti neresidir? | Bilgi tabanı dışında olduğu için cevap vermemeli | ✅ Başarılı |
| 7 | Bugün hava nasıl? | Bilgi tabanı dışında olduğu için cevap vermemeli | ✅ Başarılı |
| 8 | Boş sorgu | Kullanıcıdan soru girmesini istemeli | ✅ Başarılı |

## Retrieval Güvenliği

Sistemde `0.35` cosine similarity eşik değeri kullanılmaktadır.

En alakalı doküman parçasının benzerlik skoru bu değerin altında
kalırsa yerel LLM çağrılmaz ve sistem:

> Bu bilgi sağlanan belgelerde bulunamadı.

yanıtını döndürür.

Bu kontrol, modelin kendi genel bilgisini kullanarak kaynak dışı
cevap üretmesini azaltmak amacıyla eklenmiştir.

## Gözlemler

- Türkçe sorular İngilizce Microsoft dokümanlarıyla semantik olarak eşleştirilebildi.
- Qwen3 Embedding 0.6B ile cosine similarity tabanlı retrieval gerçekleştirildi.
- SQLite içinde doküman parçaları ve embedding vektörleri saklandı.
- Her sorguda en alakalı üç doküman parçası getirildi.
- Kaynak adı, chunk numarası ve benzerlik skoru kullanıcı arayüzünde görüntülenmektedir.
- Qwen3.5 0.8B küçük ve yerel çalıştığı için bazı Türkçe cevaplarda dil kalitesi daha büyük modellere göre sınırlıdır.