const puppeteer = require('puppeteer')
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
  let preco = await page.$(".catalog-detail-price-value")
  let preco_produto = await (await preco.getProperty('textContent')).jsonValue()
  preco_produto = preco_produto.replace(',', '.')
  preco_produto = parseFloat(preco_produto.replace('R$', ''))
  console.log(preco_produto)
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




