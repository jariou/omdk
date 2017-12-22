/*
	sudo apt-get install nuget
	nuget install NDesk.Options
*/

using System;
using System.Collections.Generic;
// using System.Data;
using System.Text;
using System.Text.RegularExpressions;
using System.IO;

using System.Linq;
using System.Xml.Schema;
using System.Xml.Linq;
using NDesk.Options;

//using mono.Options;

// Hello1.cs
public class xmltransformer
{
	//public bool EnableDocumentFunction { get; set; } = true;
	static bool seqence_no = false;	
	static int row_id = 0;
	struct Upx
	{
		public bool outputrectype60;
		public int startrectype63;
		public int startrectype64;
	};

	public enum RowDelimit
	{
		Default,
		NewLine,
		Space,
		Ambescent,
		Dollar
	}

	public enum ColumnDelimit
	{
		Default,
		Comma,
		TabSpace,
		Percentage,
		OrSymbol,
		Dot
	}

	public static ColumnDelimit ColumnDelimiter { set; get; }

	public static void FetchRowSeparater(RowDelimit delimit, out string separater)
	{
		switch (delimit)
		{
			case RowDelimit.NewLine:
			case RowDelimit.Default:
			separater = Environment.NewLine;
			break;
			case RowDelimit.Space:
			separater = " ";
			break;
			case RowDelimit.Dollar:
			separater = "$";
			break;
			case RowDelimit.Ambescent:
			separater = "&";
			break;
			default:
			separater = Environment.NewLine;
			break;
		}
	}

	public static void FetchColumnSeparater(ColumnDelimit delimit, out string separater)
	{
		switch (delimit)
		{
			case ColumnDelimit.Comma:
			case ColumnDelimit.Default:
			separater = ",";
			break;
			case ColumnDelimit.Dot:
			separater = ".";
			break;
			case ColumnDelimit.OrSymbol:
			separater = "|";
			break;
			case ColumnDelimit.Percentage:
			separater = "%";
			break;
			case ColumnDelimit.TabSpace:
			separater = "\t";
			break;
			default:
			separater = ",";
			break;
		}
	}

	static void converttoupx(XDocument doc, string outputcsv, string datatag, RowDelimit rdelimit, ColumnDelimit cdelimit, bool outputheader,ref Upx upx)
	{
		StringBuilder builder = new StringBuilder();
		string Rowseparater = string.Empty;
		FetchRowSeparater(rdelimit, out Rowseparater);

		string Columnseparater = string.Empty;
		FetchColumnSeparater(cdelimit, out Columnseparater);

		if (upx.startrectype63 == 0)
		{
			foreach (XElement data in doc.Descendants(datatag))
			{

				bool first = true;
				int i = 0;
				foreach (XAttribute innerval in data.Attributes())
				{
					if (innerval.Name == "RecTypeCode63")
					{
						upx.startrectype63 = i;
					}
					if (innerval.Name == "RecTypeCode64")
					{
						upx.startrectype64 = i;

					}
					if (first == true) first = false;
					i++;
				}
				break;
			}
		}


		foreach (XElement data in doc.Descendants(datatag))
		{
			int i = 0;
			bool first = true;
			foreach (XAttribute innerval in data.Attributes())
			{
				if (upx.outputrectype60 == false && i < upx.startrectype63 )
				{
					if (first == true)
					{
						builder.Append("***1,13.0.0,20150421,XXXXXXX,OASIS,XXXXXXX,XXXXXX,UPX from LocFile,XXX,TBD,Hurricane,X,ML,USD,");
						builder.Append(Rowseparater);
						first = false;
					}
					else builder.Append(Columnseparater);
					builder.Append(innerval.Value);
				}
				if (upx.outputrectype60 == false && i == upx.startrectype63 )
				{
					upx.outputrectype60 = true;
					builder.Append(Rowseparater);
					first = true;
				}
				if (i >= upx.startrectype63 && i < upx.startrectype64)
				{
					if (first == true) first = false;
					else builder.Append(Columnseparater);
					builder.Append(innerval.Value);
				}

				if (i == upx.startrectype64)
				{
					builder.Append(Rowseparater);
					first = true;
				}
				if (i >= upx.startrectype64)
				{
					if (first == true) first = false;
					else builder.Append(Columnseparater);
					builder.Append(innerval.Value);
				}
				i++;
			}
			builder.Append(Rowseparater);
		}

		File.AppendAllText(outputcsv, builder.ToString());

	}


	static void converttocsv(XDocument doc, string outputcsv, string datatag, RowDelimit rdelimit, ColumnDelimit cdelimit, bool outputheader)
	{
		StringBuilder builder = new StringBuilder();
		string Rowseparater = string.Empty;
		FetchRowSeparater(rdelimit, out Rowseparater);

		string Columnseparater = string.Empty;
		FetchColumnSeparater(cdelimit, out Columnseparater);

		if (outputheader == true)
		{

			foreach (XElement data in doc.Descendants(datatag))
			{
				bool first = true;
				foreach (XAttribute innerval in data.Attributes())
				{
					if (first == true) { 
						first = false;
						if (seqence_no == true) {
							builder.Append("ROW_ID,");
						}
					}
					else builder.Append(Columnseparater);
					builder.Append(innerval.Name);
				}
				builder.Append(Rowseparater);
				break;
			}

		}

		foreach (XElement data in doc.Descendants(datatag))
		{
			bool first = true;
			foreach (XAttribute innerval in data.Attributes())
			{
				if (first == true) {
					first = false;
					if (seqence_no == true) {						
						builder.Append(row_id);
						builder.Append(Columnseparater);
						row_id++;
					}
				}
				else builder.Append(Columnseparater);
				builder.Append(innerval.Value);
			}
			builder.Append(Rowseparater);
		}

		File.AppendAllText(outputcsv, builder.ToString());
	}

	public static XDocument ConvertCsvToXML(string csvString, string[] separatorField)
	{
		//split the rows
		var sep = new[] { "\r\n" };
		string[] rows = csvString.Split(sep, StringSplitOptions.RemoveEmptyEntries);
		//Create the declaration
		var xsurvey = new XDocument(
			new XDeclaration("1.0", "UTF-8", "yes"));
		var xroot = new XElement("root"); //Create the root
		for (int i = 0; i < rows.Length; i++)
		{
			//Create each row
			if (i > 0)
			{
				xroot.Add(rowCreator(rows[i], rows[0], separatorField));
			}
		}
		xsurvey.Add(xroot);
		return xsurvey;
	}

	private static string[] SplitCSVstring(string input)
    {
        Regex csvSplit = new Regex("(?:^|,)(\"(?:[^\"]+|\"\")*\"|[^,]*)", RegexOptions.Compiled);
        return csvSplit.Matches(input).Cast<Match>().Select(m => m.Value).ToArray();         
    }

	private static XElement rowCreator(string row,
		string firstRow, string[] separatorField)
	{
		string[] temp = SplitCSVstring(row);
		// string[] temp = row.Split(separatorField, StringSplitOptions.None);
		string[] names = firstRow.Split(separatorField, StringSplitOptions.None);
		var xrow = new XElement("rec");
		for (int i = 0; i < temp.Length; i++)
		{
			if (i > 0) temp[i] = temp[i].Substring(1);
			if (temp[i].Length > 0)
			{
				xrow.Add(new XAttribute(names[i], temp[i]));
			}
		}
		return xrow;
	}

	// Code for input validation
	static int Idoit(string csv, string xsltstr, string outputcsvfile, bool outputheader, string xsdstr, out string firstErrors)
	{

		XDocument doc = ConvertCsvToXML(csv, new[] { "," });

		Upx upx;
		upx.startrectype63 = 0;
		upx.startrectype64 = 0;
		upx.outputrectype60 = false;
	
		firstErrors = "";
		if (outputheader == true && xsdstr.Length > 0)
		{
			int errorcount = 0;
			string errstr = "";
			XmlSchemaSet schemas = new XmlSchemaSet();
			schemas.Add("", System.Xml.XmlReader.Create(new StringReader(xsdstr)));

			doc.Validate(schemas, (o, e) =>
			{
					// Console.WriteLine("{0}", e.Message);
				if (e.Message.IndexOf("attribute is not declared") == -1) {
					if (errorcount < 20) {
						errstr += e.Message + "\n";
					}
					errorcount++;
				}

				});

			if (errorcount > 0)
			{
				firstErrors = errstr;
				Console.WriteLine (errstr);
				return errorcount;
			}
		}

		XDocument newDoc = new XDocument();

		using (System.Xml.XmlWriter writer = newDoc.CreateWriter())
		{
			System.Xml.Xsl.XslCompiledTransform xslt = new System.Xml.Xsl.XslCompiledTransform();
			System.Xml.Xsl.XsltSettings settings = new System.Xml.Xsl.XsltSettings() { EnableDocumentFunction = true };
			xslt.Load(System.Xml.XmlReader.Create(new StringReader(xsltstr)), settings, new System.Xml.XmlUrlResolver());
			xslt.Transform(doc.CreateReader(), writer);
			//System.Xml.Xsl.XslCompiledTransform xslt = new System.Xml.Xsl.XslCompiledTransform();
			//xslt.Load(System.Xml.XmlReader.Create(new StringReader(xsltstr)));
			//xslt.Transform(doc.CreateReader(), writer);
		}

		string ext = Path.GetExtension(outputcsvfile);
		if (ext == ".csv")
		{
			converttocsv(newDoc, outputcsvfile, "rec", RowDelimit.NewLine, ColumnDelimit.Comma, outputheader);
		}
		if (ext == ".upx")
		{
			Console.WriteLine ("=======GENERATING UPX=========");
			converttoupx(newDoc, outputcsvfile, "rec", RowDelimit.NewLine, ColumnDelimit.Comma, outputheader,ref upx);
		}
		
		return 0;

	}


	// parameters:
	// inputcsvfile - input csvfile
	// xsltfile - xslt tarnsformation file
	// xsdfile - xsdfile for validatiing input - if empty string don't bother validating
	// outputcsvfile
	static int Ibatchrun(string inputcsvfile, string xsltfile, string xsdfile, string outputcsvfile, out string firsterrors)
	{
		StringBuilder sb = new StringBuilder();

		bool outputheader = true;
		string xsltstr = File.ReadAllText(xsltfile);
		string xsdstr = "";
		if (xsdfile.Length > 0) xsdstr = File.ReadAllText(xsdfile);
		int chunkno = 0;
		int ret = 0;
		using (StreamReader r = new StreamReader(inputcsvfile))
		{
			int i = 0;

			string nextLine = null;
			string firstLine = r.ReadLine();
			if (firstLine != null)
			{
				sb.Append(firstLine);
				sb.Append("\r\n");
				nextLine = r.ReadLine();
			}

			while (nextLine != null)
			{
				sb.Append(nextLine);
				sb.Append("\r\n");
				if (i == 50000)
				{
					Console.WriteLine("Processing chunk {0}...", chunkno);
					firsterrors = "";
					ret = Idoit(sb.ToString(), xsltstr, outputcsvfile, outputheader, xsdstr, out firsterrors);
					if (outputheader == true) outputheader = false;
					sb = new StringBuilder();
					sb.Append(firstLine);
					sb.Append("\r\n");
					i = 0;
					chunkno++;
				}
				nextLine = r.ReadLine();
				i++;
			}
			Console.WriteLine("Processing chunk {0}...", chunkno);
			firsterrors = "";
			ret = Idoit(sb.ToString(), xsltstr, outputcsvfile, outputheader, xsdstr, out firsterrors);

				// process xml
			return i;
		}
	}

	public static string iapplyxslt( string csvinfile, string xsltfile, string xsdfile, string outputcsvfile) 
	{
		string firsterrors = "";
			// batchrun(csvinfile,  xsltfile,  outputcsvfile)	;
		int i = Ibatchrun(csvinfile,  xsltfile, xsdfile, outputcsvfile, out firsterrors);
		if (firsterrors.Length == 0) firsterrors = "Done";
		return  firsterrors;
	}

	static void ShowHelp (OptionSet p)
    {

        Console.WriteLine ("Options:");
        p.WriteOptionDescriptions (Console.Out);
        Environment.Exit(0);
    }

    
   public static void Main(string[] args)
   {
   	
   	 bool show_help = false;

   	 string csvfilename = "" ;
     string xsdfilename = "" ;
     string xsltfilename = "" ;
     string outputfilename = "" ;

    
        var p = new OptionSet () {
            { "d|xsd=", "xsd file name",
              v =>  xsdfilename = v  },
            { "c|csv=", "csv file name",
              v => { 
              	csvfilename=v; 
              	} },
            { "t|xslt=", "xslt file name",
              v => xsltfilename = v },
            { "o|output=", "output file name",
              v => outputfilename = v },
            { "s", "Add sequence number column",  v =>  seqence_no = true },
            { "h|help",  "show this message and exit", v => show_help = true },
        };

        List<string> extra;
        try {
            extra = p.Parse (args);
        }
        catch (OptionException e) {
            Console.Write ("xtrans: ");
            Console.WriteLine (e.Message);
            Console.WriteLine ("Try `xtrans --help' for more information.");
            return;
        }


        if (show_help) {
        	ShowHelp (p);
        }
        Console.WriteLine ("================");
        Console.WriteLine(csvfilename);
        Console.WriteLine ("================");

        if (csvfilename == "") {
        	Console.WriteLine ("Error: CSV file name not supplied");
        	ShowHelp (p);
        }

        if (xsltfilename == "") {
        	Console.WriteLine ("Error: xslt file name not supplied");
        	ShowHelp (p);
        }

        if (outputfilename == "") {
        	Console.WriteLine ("Error: output file name not supplied");
        	ShowHelp (p);
        }


        // Console.WriteLine (message, name);
		row_id  =1;        
        string s = iapplyxslt(csvfilename,xsltfilename,xsdfilename,outputfilename);
   		// string s = iapplyxslt("SourceLoc.csv","MappingMapToCanLocARA.xslt","CanLocARA.xsd","output.csv");
   		// string s = iapplyxslt("SourceLoc.csv","MappingMapToCanLocARA.xslt","","output.csv");
   		// System.Console.WriteLine(s);
   }
}
