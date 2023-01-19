const puppeteer = require('puppeteer')
//const $ = require('cheerio')
//const CronJob = require('cron').CronJob
//const nodemailer = require('nodemailer')

//const url = 'https://www.amazon.com.br/gp/product/B07BJLPDQ5/ref=ox_sc_saved_title_9?smid=A1ZZFT5FULY4LN&psc=1/';
//const url = 'https://shopee.com.br/P%C3%B3-Focallure-Solto-Em-3-Cores-Controle-De-Oleosidade-Suave-Maquiagem-Facial-i.253544235.7695994580?sp_atk=4489ae37-0ee9-4a17-aecf-4d03a0082dc1&xptdk=4489ae37-0ee9-4a17-aecf-4d03a0082dc1'
//const url = 'https://pt.aliexpress.com/item/1005001802881165.html?pdp_ext_f=%7B%22ship_from%22:%22CN%22,%22sku_id%22:%2212000028067501017%22%7D&&scm=1007.25281.272534.0&scm_id=1007.25281.272534.0&scm-url=1007.25281.272534.0&pvid=5e21a0ba-e49e-4a22-ba6b-77950d351cdf&utparam=%257B%2522process_id%2522%253A%252256%2522%252C%2522x_object_type%2522%253A%2522product%2522%252C%2522pvid%2522%253A%25225e21a0ba-e49e-4a22-ba6b-77950d351cdf%2522%252C%2522belongs%2522%253A%255B%257B%2522floor_id%2522%253A%252230904758%2522%252C%2522id%2522%253A%252231580078%2522%252C%2522type%2522%253A%2522dataset%2522%257D%252C%257B%2522id_list%2522%253A%255B%25221000294769%2522%255D%252C%2522type%2522%253A%2522gbrain%2522%257D%255D%252C%2522pageSize%2522%253A%252220%2522%252C%2522language%2522%253A%2522pt%2522%252C%2522scm%2522%253A%25221007.25281.272534.0%2522%252C%2522countryId%2522%253A%2522BR%2522%252C%2522scene%2522%253A%2522TopSelection-Waterfall%2522%252C%2522tpp_buckets%2522%253A%252221669%25230%2523265320%252371_21669%25234190%252319162%2523450_15281%25230%2523272534%25230%2522%252C%2522x_object_id%2522%253A%25221005001802881165%2522%257D&pdp_npi=2%40dis%21BRL%21R%24%201.120%2C08%21R%24%20672%2C03%21%21%21%21%21%402105267916598486608715787e84b6%2112000028067501017%21gdf&spm=a2g0o.plus.pick.item2&aecmd=true'
//const url = 'https://www.dafiti.com.br/Camiseta-LAB86-Stranger-Things-Verde-11538041.html'

const url = process.argv[2]
monitor()
async function monitor()
{
  let page = await configurar()
  await rastrear_site(page)
}
async function configurar()
{
  const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto(url);
  return page;
}

async function rastrear_site(page)
{
  try
  {
  await page.reload();
  let html = await page.evaluate(() => document.body.innerHTML);
  //console.log(html);

  const titulo = await page.$(".product-name")  // works for aliexpress and amazon. does not work for shopee.
                                                // html class name or id (for the title):
                                                //                                      aliexpress = .product-title-text
                                                //                                      amazon = #productTitle
  //let preco = await page.$(".catalog-detail-price-value")
  //const descricao = await page.$(".product-information-description")
  let titulo_produto = await (await titulo.getProperty('textContent')).jsonValue()
  //let descricao_produto = await (await descricao.getProperty('textContent')).jsonValue()
  //let preco_produto = await (await preco.getProperty('textContent')).jsonValue()
  //preco_produto = preco_produto.replace(',', '.')
  //preco_produto = parseFloat(preco_produto.replace('R$', ''))
  console.log(titulo_produto)
  //console.log(descricao_produto)
  //console.log(preco_produto)
  }
  catch (e)
  {
    console.log(e)
  } finally
  {
    await page.close()
    process.exit()
  }
}




