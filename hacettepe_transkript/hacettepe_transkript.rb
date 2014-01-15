#!/usr/bin/ruby

require 'net/http'

require 'haml'
require 'nokogiri'
require 'unicode_utils'

USER = hidepy467f6a8381f9977f83dc7525a084099fca12a03ddcf971232d6232a905452fad
PASS = hidepy59f9723fee3e4fd86143494c1290197c54a33ba1039a74d9f244d1c7d15ecddc

class Transcript
	def initialize(user, pass)
		@user = user.freeze
		@pass = pass.freeze
	end

	def sec_code
		@sec_code ||= fetch_security_code
	end

	def info
		@transcript_page ||= fetch_transcript_page
		@info ||= parse_info
		@info
	end

	def terms
		@transcript_page ||= fetch_transcript_page
		@terms ||= parse_terms
		@terms
	end

	def lessons
		terms.values.map{ |i| i[:lessons] }.flatten.freeze
	end

	def refetch_transcript
		@transcript_page = fetch_transcript_page
	end

	private

	def fetch_security_code
		uri = URI 'http://www.oid.hacettepe.edu.tr/cgi-bin/menu.cgi'
		params = { :login => @user, 
			       :passwd => @pass, 
			       :SubmitName => :Tamam }
		res = Net::HTTP.post_form(uri, params)
		doc = Nokogiri::HTML(res.body)
		doc.xpath('//input[@name="p_SECURITYCODE"]').first[:value].freeze
	end

	def fetch_transcript_page
		uri = URI 'http://www.oid.hacettepe.edu.tr/cgi-bin/transkript.cgi'
		params = { :p_UserCode => @user, 
				   :p_AccessCode => 1,
		 		   :p_AccessDetail => :YOK,
		 		   :p_SECURITYCODE => sec_code }
		res = Net::HTTP.post_form(uri, params)

		text = res.body.encode("utf-8", "iso-8859-9")
		(Nokogiri::HTML text).freeze
	end

	def parse_terms
		terms = {}
		term = ""

		elems = @transcript_page.xpath('/html/body/table[2]//tr/td')
		elems.each do |i|
			case i[:valign] 
			when "top"
				case i[:colspan] 
				when "2" then 
					lesson = i.text.delete!("\xC2\xA0")
					terms[term][:lessons] << {:id => lesson, :other => []}
				when nil then
					terms[term][:lessons].last[:other] << i.text.delete("\xC2\xA0")
				when "3" then
					re = /(?<=Dönem Akademik Ortalaması : ).*/
					terms[term][:tpa] = i.text[re].to_f
				when "6" then
					re = /(?<=Genel Akademik Ortalama : ).*/
					terms[term][:gpa] = i.text[re].to_f
				end
			when "middle"
				case i[:colspan] 
				when "3" then
					term = i.text.delete("\xC2\xA0")[/(?<=Akademik Dönem : ).*/]
					terms[term] = { :lessons => [] }
				end
			end
		end

		terms.each do |term_name, term|
			term[:lessons].each do |lesson|
				lesson[:name] = lesson[:other][0]
				lesson[:t] = lesson[:other][1].to_i
				lesson[:p] = lesson[:other][2].to_i
				lesson[:c] = lesson[:other][3].to_i
				lesson[:letter] = lesson[:other][4]
				lesson.delete :other
				lesson.freeze
			end
			term[:lessons].sort_by! { |i| i[:letter] }
			term[:lessons].freeze
			term.freeze
		end
	end
	
	def parse_info
		info = {}
		elems = @transcript_page.xpath('/html/body/table[1]/tr/td').map { |i| i.text }
		elems.each_with_index do |el, i|
			if el == ":"
				info[elems[i-1]] = UnicodeUtils.titlecase elems[i+1] 
				info[elems[i-1]].delete!("" << 775) # Hack to lowercasing "İ" > "i"
			end
		end
		info["name"] = info['Soyadı, Adı'].split(", ").reverse * " "
		info["gpa"] = info["Akademik Ortalaması"]
		info
	end
end

Haml::Options.defaults[:format] = :html5
haml = Haml::Engine.new(File.read("template.haml"))

puts haml.render(Object.new, t: Transcript.new(USER, PASS))
